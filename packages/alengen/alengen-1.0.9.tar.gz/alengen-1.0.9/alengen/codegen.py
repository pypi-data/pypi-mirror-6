"""Contains the code generation logic and helper functions."""

from collections import defaultdict
from keyword import iskeyword
import sys
import re

from sqlalchemy import (Enum, ForeignKeyConstraint, PrimaryKeyConstraint, CheckConstraint, UniqueConstraint, Table,
                        Column)
from sqlalchemy.util import OrderedDict
from sqlalchemy.types import Boolean, String
import sqlalchemy

try:
    from sqlalchemy.sql.expression import TextClause
except ImportError:
    # SQLAlchemy < 0.8
    from sqlalchemy.sql.expression import _TextClause as TextClause

_re_boolean_check_constraint = re.compile(r"(?:(?:.*?)\.)?(.*?) IN \(0, 1\)")
_re_column_name = re.compile(r'(?:(["`])(?:.*)\1\.)?(["`]?)(.*)\2')
_re_enum_check_constraint = re.compile(r"(?:(?:.*?)\.)?(.*?) IN \((.+)\)")
_re_enum_item = re.compile(r"'(.*?)(?<!\\)'")


class _DummyInflectEngine(object):
    def singular_noun(self, noun):
        return noun


def _get_compiled_expression(statement):
    """Returns the statement in a form where any placeholders have been filled in."""
    if isinstance(statement, TextClause):
        return statement.text

    dialect = statement.left.table.bind.dialect
    compiler = statement._compiler(dialect)

    # Adapted from http://stackoverflow.com/a/5698357/242021
    class LiteralCompiler(compiler.__class__):
        def visit_bindparam(self, bindparam, within_columns_clause=False, literal_binds=False, **kwargs):
            return super(LiteralCompiler, self).render_literal_bindparam(
                bindparam, within_columns_clause=within_columns_clause,
                literal_binds=literal_binds, **kwargs
            )

    compiler = LiteralCompiler(dialect, statement)
    return compiler.process(statement)


def _get_constraint_sort_key(constraint):
    if isinstance(constraint, CheckConstraint):
        return 'C{0}'.format(constraint.sqltext)
    return constraint.__class__.__name__[0] + repr(constraint.columns)


def _get_common_fk_constraints(table1, table2):
    """Returns a set of foreign key constraints the two tables have against each other."""
    c1 = set(c for c in table1.constraints if isinstance(c, ForeignKeyConstraint) and
                                              c.elements[0].column.table == table2)
    c2 = set(c for c in table2.constraints if isinstance(c, ForeignKeyConstraint) and
                                              c.elements[0].column.table == table1)
    return c1.union(c2)


def _render_column_type(coltype):
    args = []
    if isinstance(coltype, Enum):
        args.extend(repr(arg) for arg in coltype.enums)
        if coltype.name is not None:
            args.append('name={0!r}'.format(coltype.name))

    text = coltype.__class__.__name__
    if args:
        text += '({0})'.format(', '.join(args))

    return text


def _render_fk(fk):
    text = "ForeignKey('%s.%s'" % (fk.column.table.fullname, fk.column.name)
    if fk.deferrable:
        text += ', deferrable=True'
    if fk.initially:
        text += ', initially=%r' % fk.initially
    return text + ')'


def _render_column(column, show_name):
    kwarg = []
    is_sole_pk = column.primary_key and len(column.table.primary_key) == 1
    dedicated_fks = [c for c in column.foreign_keys if len(c.constraint.columns) == 1]
    is_unique = any(isinstance(c, UniqueConstraint) and set(c.columns) == {column}
                    for c in column.table.constraints)
    has_index = any(set(i.columns) == {column} for i in column.table.indexes)

    # Render the column type if there are no foreign keys on it or any of them points back to itself
    render_coltype = not dedicated_fks or any(fk.column is column for fk in dedicated_fks)

    if column.key != column.name:
        kwarg.append('key')
    if column.primary_key:
        kwarg.append('primary_key')
    if not column.nullable and not is_sole_pk:
        kwarg.append('nullable')
    if is_unique:
        column.unique = True
        kwarg.append('unique')
    elif has_index:
        column.index = True
        kwarg.append('index')
    if column.server_default and not is_sole_pk:
        column.server_default = _get_compiled_expression(column.server_default.arg)
        kwarg.append('server_default')

    return 'Column({0})'.format(', '.join(
        ([repr(column.name)] if show_name else []) +
        ([_render_column_type(column.type)] if render_coltype else []) +
        [_render_fk(x) for x in dedicated_fks] +
        [repr(x) for x in column.constraints] +
        ['{0}={1}'.format(k, repr(getattr(column, k))) for k in kwarg]))


def _render_constraint(constraint):
    if isinstance(constraint, ForeignKeyConstraint):
        local_columns = constraint.columns
        remote_columns = ['{0}.{1}'.format(fk.column.table.fullname, fk.column.name)
                          for fk in constraint.elements]
        return 'ForeignKeyConstraint({0!r}, {1!r})'.format(local_columns, remote_columns)
    elif isinstance(constraint, CheckConstraint):
        return 'CheckConstraint({0!r})'.format(_get_compiled_expression(constraint.sqltext))
    elif isinstance(constraint, UniqueConstraint):
        columns = [repr(col.name) for col in constraint.columns]
        return 'UniqueConstraint({0})'.format(', '.join(columns))


def _render_index(index):
    columns = [repr(col.name) for col in index.columns]
    return 'Index({0!r}, {1})'.format(index.name, ', '.join(columns))


class ImportCollector(OrderedDict):
    def add_import(self, obj):
        type_ = type(obj) if not isinstance(obj, type) else obj
        pkgname = 'sqlalchemy' if type_.__name__ in sqlalchemy.__all__ else type_.__module__
        self.add_literal_import(pkgname, type_.__name__)

    def add_literal_import(self, pkgname, name):
        names = self.setdefault(pkgname, set())
        names.add(name)

    def render(self):
        return '\n'.join('from {0} import {1}'.format(package, ', '.join(sorted(names)))
                         for package, names in list(self.items()))


class Model(object):
    def __init__(self, table):
        super(Model, self).__init__()
        self.table = table
        self.schema = table.schema

        # Adapt column types to the most reasonable generic types (ie. VARCHAR -> String)
        for column in table.columns:
            cls = column.type.__class__
            for supercls in cls.__mro__:
                if hasattr(supercls, '__visit_name__'):
                    cls = supercls
                if supercls.__name__ != supercls.__name__.upper() and not supercls.__name__.startswith('_'):
                    break

            column.type = column.type.adapt(cls)

    def add_imports(self, collector):
        if self.table.columns:
            collector.add_import(Column)

        for column in self.table.columns:
            collector.add_import(column.type)

        for constraint in sorted(self.table.constraints, key=_get_constraint_sort_key):
            if isinstance(constraint, ForeignKeyConstraint):
                if len(constraint.columns) > 1:
                    collector.add_literal_import('sqlalchemy', 'ForeignKeyConstraint')
                else:
                    collector.add_literal_import('sqlalchemy', 'ForeignKey')
            elif isinstance(constraint, UniqueConstraint):
                if len(constraint.columns) > 1:
                    collector.add_literal_import('sqlalchemy', 'UniqueConstraint')
            elif not isinstance(constraint, PrimaryKeyConstraint):
                collector.add_import(constraint)

        for index in self.table.indexes:
            if len(index.columns) > 1:
                collector.add_import(index)


class ModelTable(Model):
    def add_imports(self, collector):
        super(ModelTable, self).add_imports(collector)
        collector.add_import(Table)

    def render(self):
        text = 't_{0} = Table(\n    {0!r}, metadata,\n'.format(self.table.name)

        for column in self.table.columns:
            text += '    {0},\n'.format(_render_column(column, True))

        for constraint in sorted(self.table.constraints, key=_get_constraint_sort_key):
            if isinstance(constraint, PrimaryKeyConstraint):
                continue
            if isinstance(constraint, (ForeignKeyConstraint, UniqueConstraint)) and len(constraint.columns) == 1:
                continue
            text += '    {0},\n'.format(_render_constraint(constraint))

        for index in self.table.indexes:
            if len(index.columns) > 1:
                text += '    {0},\n'.format(_render_index(index))

        if self.schema:
            text += "    schema='{0}',\n".format(self.schema)

        return text.rstrip('\n,') + '\n)'


class ModelClass(Model):
    parent_name = 'Base'

    def __init__(self, table, association_tables, inflect_engine, detect_joined):
        super(ModelClass, self).__init__(table)
        self.name = self._tablename_to_classname(table.name, inflect_engine)
        self.children = []
        self.attributes = OrderedDict()

        # Assign attribute names for columns
        for column in table.columns:
            attrname = column.name + '_' if iskeyword(column.name) else column.name
            self.attributes[attrname] = column

        # Add many-to-one relationships
        pk_column_names = set(col.name for col in table.primary_key.columns)
        for constraint in sorted(table.constraints, key=_get_constraint_sort_key):
            if isinstance(constraint, ForeignKeyConstraint):
                target_cls = self._tablename_to_classname(constraint.elements[0].column.table.name, inflect_engine)
                if detect_joined and self.parent_name == 'Base' and set(constraint.columns) == pk_column_names:
                    self.parent_name = target_cls
                else:
                    self._add_relationship(ManyToOneRelationship(self.name, target_cls, constraint, inflect_engine))

        # Add many-to-many relationships
        for association_table in association_tables:
            fk_constraints = [c for c in association_table.constraints if isinstance(c, ForeignKeyConstraint)]
            fk_constraints.sort(key=_get_constraint_sort_key)
            target_cls = self._tablename_to_classname(fk_constraints[1].elements[0].column.table.name, inflect_engine)
            self._add_relationship(ManyToManyRelationship(self.name, target_cls, association_table))

    @staticmethod
    def _tablename_to_classname(tablename, inflect_engine):
        #camel_case_name = ''.join(part.capitalize() for part in tablename.split('_'))
        #return inflect_engine.singular_noun(camel_case_name) or camel_case_name
        return tablename

    def _add_relationship(self, relationship):
        for attrname in relationship.suggested_names:
            if attrname not in self.attributes and not iskeyword(attrname):
                self.attributes[attrname] = relationship
                break

    def add_imports(self, collector):
        super(ModelClass, self).add_imports(collector)

        if any(isinstance(value, Relationship) for value in list(self.attributes.values())):
            collector.add_literal_import('sqlalchemy.orm', 'relationship')

        for child in self.children:
            child.add_imports(collector)

    def render(self):
        text = 'class {0}({1}):\n'.format(self.name, self.parent_name)
        text += '    __tablename__ = {0!r}\n'.format(self.table.name)

        # Render constraints and indexes as __table_args__
        table_args = []
        for constraint in sorted(self.table.constraints, key=_get_constraint_sort_key):
            if isinstance(constraint, PrimaryKeyConstraint):
                continue
            if isinstance(constraint, (ForeignKeyConstraint, UniqueConstraint)) and len(constraint.columns) == 1:
                continue
            table_args.append(_render_constraint(constraint))
        for index in self.table.indexes:
            if len(index.columns) > 1:
                table_args.append(_render_index(index))

        table_kwargs = {}
        if self.schema:
            table_kwargs['schema'] = self.schema

        kwargs_items = ', '.join('{0!r}: {1!r}'.format(key, table_kwargs[key]) for key in table_kwargs)
        kwargs_items = '{{{0}}}'.format(kwargs_items) if kwargs_items else None
        if table_kwargs and not table_args:
            text += '    __table_args__ = {0}\n'.format(kwargs_items)
        elif table_args:
            if kwargs_items:
                table_args.append(kwargs_items)
            if len(table_args) == 1:
                table_args[0] += ','
            text += '    __table_args__ = (\n        {0}\n    )\n'.format(',\n        '.join(table_args))

        # Render columns
        text += '\n'
        for attr, column in list(self.attributes.items()):
            if isinstance(column, Column):
                show_name = attr != column.name
                text += '    {0} = {1}\n'.format(attr, _render_column(column, show_name))

        # Render relationships
        if any(isinstance(value, Relationship) for value in list(self.attributes.values())):
            text += '\n'
        for attr, relationship in list(self.attributes.items()):
            if isinstance(relationship, Relationship):
                text += '    {0} = {1}\n'.format(attr, relationship.render())

        # Render subclasses
        for child_class in self.children:
            text += '\n\n' + child_class.render()

        return text


class Relationship(object):
    def __init__(self, source_cls, target_cls):
        super(Relationship, self).__init__()
        self.source_cls = source_cls
        self.target_cls = target_cls
        self.kwargs = OrderedDict()

    @property
    def suggested_names(self):
        yield self.preferred_name if not iskeyword(self.preferred_name) else self.preferred_name + '_'

        iteration = 0
        while True:
            iteration += 1
            yield self.preferred_name + str(iteration)

    def render(self):
        text = 'relationship('
        args = [repr(self.target_cls)]

        if 'secondaryjoin' in self.kwargs:
            text += '\n        '
            delimiter, end = ',\n        ', '\n    )'
        else:
            delimiter, end = ', ', ')'

        args.extend([key + '=' + value for key, value in list(self.kwargs.items())])
        return text + delimiter.join(args) + end


class ManyToOneRelationship(Relationship):
    def __init__(self, source_cls, target_cls, constraint, inflect_engine):
        super(ManyToOneRelationship, self).__init__(source_cls, target_cls)

        colname = constraint.columns[0]
        tablename = constraint.elements[0].column.table.name
        if not colname.endswith('_id'):
            self.preferred_name = inflect_engine.singular_noun(tablename) or tablename
        else:
            self.preferred_name = colname[:-3]

        # Add uselist=False to One-to-One relationships
        if any(isinstance(c, (PrimaryKeyConstraint, UniqueConstraint)) and
                               set(col.name for col in c.columns) == set(constraint.columns)
               for c in constraint.table.constraints):
            self.kwargs['uselist'] = 'False'

        # Handle self referential relationships
        if source_cls == target_cls:
            self.preferred_name = 'parent' if not colname.endswith('_id') else colname[:-3]
            pk_col_names = [col.name for col in constraint.table.primary_key]
            self.kwargs['remote_side'] = '[{0}]'.format(', '.join(pk_col_names))

        # If the two tables share more than one foreign key constraint,
        # SQLAlchemy needs an explicit primaryjoin to figure out which column(s) to join with
        common_fk_constraints = _get_common_fk_constraints(constraint.table, constraint.elements[0].column.table)
        if len(common_fk_constraints) > 1:
            self.kwargs['primaryjoin'] = "'{0}.{1} == {2}.{3}'".format(source_cls, constraint.columns[0], target_cls,
                                                                       constraint.elements[0].column.name)


class ManyToManyRelationship(Relationship):
    def __init__(self, source_cls, target_cls, assocation_table):
        super(ManyToManyRelationship, self).__init__(source_cls, target_cls)

        self.kwargs['secondary'] = repr(assocation_table.name)
        constraints = [c for c in assocation_table.constraints if isinstance(c, ForeignKeyConstraint)]
        constraints.sort(key=_get_constraint_sort_key)
        colname = constraints[1].columns[0]
        tablename = constraints[1].elements[0].column.table.name
        self.preferred_name = tablename if not colname.endswith('_id') else colname[:-3] + 's'

        # Handle self referential relationships
        if source_cls == target_cls:
            self.preferred_name = 'parents' if not colname.endswith('_id') else colname[:-3] + 's'
            pri_pairs = list(zip(constraints[0].columns, constraints[0].elements))
            sec_pairs = list(zip(constraints[1].columns, constraints[1].elements))
            pri_joins = ['{0}.{1} == {2}.c.{3}'.format(source_cls, elem.column.name, assocation_table.name, col)
                         for col, elem in pri_pairs]
            sec_joins = ['{0}.{1} == {2}.c.{3}'.format(target_cls, elem.column.name, assocation_table.name, col)
                         for col, elem in sec_pairs]
            self.kwargs['primaryjoin'] = (
                repr('and_({0})'.format(', '.join(pri_joins))) if len(pri_joins) > 1 else repr(pri_joins[0]))
            self.kwargs['secondaryjoin'] = (
                repr('and_({0})'.format(', '.join(sec_joins))) if len(sec_joins) > 1 else repr(sec_joins[0]))


class CodeGenerator(object):
    header = '# coding: utf-8'
    footer = ''

    def __init__(self, metadata, noindexes=False, noconstraints=False, nojoined=False):
        super(CodeGenerator, self).__init__()

        inflect_engine = _DummyInflectEngine()

        # Pick association tables from the metadata into their own set, don't process them normally
        links = defaultdict(lambda: [])
        association_tables = set()
        for table in list(metadata.tables.values()):
            # Link tables have exactly two foreign key constraints and all columns are involved in them
            fk_constraints = [constr for constr in table.constraints if isinstance(constr, ForeignKeyConstraint)]
            if (len(fk_constraints) == 2 and all(col.foreign_keys for col in table.columns)):
                association_tables.add(table.name)
                tablename = sorted(fk_constraints, key=_get_constraint_sort_key)[0].elements[0].column.table.name
                links[tablename].append(table)

        # Iterate through the tables and create model classes when possible
        self.models = []
        self.collector = ImportCollector()
        classes = {}
        for table in sorted(list(metadata.tables.values()), key=lambda t: (t.schema or '', t.name)):
            # Support for Alembic and sqlalchemy-migrate -- never expose the schema version tables
            if table.name in ('alembic_version', 'migrate_version'):
                continue

            if noindexes:
                table.indexes.clear()

            if noconstraints:
                table.constraints = set([table.primary_key])
                table.foreign_keys.clear()
                for col in table.columns:
                    col.foreign_keys.clear()
            else:
                # Detect check constraints for boolean and enum columns
                for constraint in table.constraints.copy():
                    if isinstance(constraint, CheckConstraint):
                        sqltext = _get_compiled_expression(constraint.sqltext)

                        # Turn any integer-like column with a CheckConstraint like "column IN (0, 1)" into a Boolean
                        match = _re_boolean_check_constraint.match(sqltext)
                        if match:
                            colname = _re_column_name.match(match.group(1)).group(3)
                            table.constraints.remove(constraint)
                            table.c[colname].type = Boolean()
                            continue

                        # Turn any string-type column with a CheckConstraint like "column IN (...)" into an Enum
                        match = _re_enum_check_constraint.match(sqltext)
                        if match:
                            colname = _re_column_name.match(match.group(1)).group(3)
                            items = match.group(2)
                            if isinstance(table.c[colname].type, String):
                                table.constraints.remove(constraint)
                                if not isinstance(table.c[colname].type, Enum):
                                    options = _re_enum_item.findall(items)
                                    table.c[colname].type = Enum(*options, native_enum=False)
                                continue

            # Only form model classes for tables that have a primary key and are not association tables
            if not table.primary_key or table.name in association_tables:
                model = ModelTable(table)
            else:
                model = ModelClass(table, links[table.name], inflect_engine, not nojoined)
                classes[model.name] = model

            self.models.append(model)
            model.add_imports(self.collector)

        # Nest inherited classes in their superclasses to ensure proper ordering
        for model in list(classes.values()):
            if model.parent_name != 'Base':
                classes[model.parent_name].children.append(model)
                self.models.remove(model)

        # Add either the MetaData or declarative_base import depending on whether there are mapped classes or not
        if not any(isinstance(model, ModelClass) for model in self.models):
            self.collector.add_literal_import('sqlalchemy', 'MetaData')
        else:
            self.collector.add_literal_import('sqlalchemy.ext.declarative', 'declarative_base')

    def render(self, outfile=sys.stdout):
        print(self.header, file=outfile)

        # Render the collected imports
        print(self.collector.render() + '\n\n', file=outfile)

        if any(isinstance(model, ModelClass) for model in self.models):
            print('Base = declarative_base()\nmetadata = Base.metadata', file=outfile)
        else:
            print('metadata = MetaData()', file=outfile)

        # Render the model tables and classes
        for model in self.models:
            print('\n\n' + model.render().rstrip('\n'), file=outfile)

        if self.footer:
            print(self.footer, file=outfile)
