#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields

STATES = {
    'readonly': "active == False",
}

SEPARATOR = ' / '


class Category(ModelSQL, ModelView):
    "Category"
    _name = "party.category"
    _description = __doc__
    name = fields.Char('Name', required=True, states=STATES)
    parent = fields.Many2One('party.category', 'Parent',
           select=1, states=STATES)
    childs = fields.One2Many('party.category', 'parent',
       'Children', states=STATES)
    active = fields.Boolean('Active')

    def __init__(self):
        super(Category, self).__init__()
        self._constraints += [
            ('check_recursion', 'recursive_categories'),
            ('check_name', 'wrong_name'),
        ]
        self._error_messages.update({
            'recursive_categories': 'You can not create recursive categories!',
            'wrong_name': 'You can not use "%s" in name field!' % SEPARATOR,
        })
        self._order.insert(1, ('name', 'ASC'))

    def default_active(self, cursor, user, context=None):
        return 1

    def check_name(self, cursor, user, ids):
        for category in self.browse(cursor, user, ids):
            if SEPARATOR in category.name:
                return False
        return True

    def get_rec_name(self, cursor, user, ids, name, arg, context=None):
        if not ids:
            return {}
        res = {}
        def _name(category):
            if category.id in res:
                return res[category.id]
            elif category.parent:
                return _name(category.parent) + SEPARATOR + category.name
            else:
                return category.name
        for category in self.browse(cursor, user, ids, context=context):
            res[category.id] = _name(category)
        return res

    def search_rec_name(self, cursor, user, name, args, context=None):
        args2 = []
        i = 0
        while i < len(args):
            if isinstance(args[i][2], basestring):
                values = args[i][2].split(SEPARATOR)
                values.reverse()
                domain = []
                field = 'name'
                for name in values:
                    domain.append((field, args[i][1], name))
                    field = 'parent.' + field
                args2.append(('id', 'inselect', self.search(cursor, user,
                    domain, order=[], context=context, query_string=True)))
            #TODO Handle list
            else:
                args2.append(('name', args[i][1], args[i][2]))
            i += 1
        return args2

Category()
