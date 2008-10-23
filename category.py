#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.osv import fields, OSV

STATES = {
    'readonly': "active == False",
}


class Category(OSV):
    "Category"
    _name = "party.category"
    _description = __doc__
    name = fields.Char('Name', required=True, states=STATES)
    parent = fields.Many2One('party.category', 'Parent',
           select=1, states=STATES)
    complete_name = fields.Function('get_complete_name',
           type="char", string='Name', states=STATES)
    childs = fields.One2Many('party.category', 'parent',
       'Childs', states=STATES)
    active = fields.Boolean('Active')

    def __init__(self):
        super(Category, self).__init__()
        self._constraints += [
            ('check_recursion', 'recursive_categories'),
        ]
        self._error_messages.update({
            'recursive_categories': 'You can not create recursive categories!',
        })
        self._order.insert(1, ('name', 'ASC'))

    def default_active(self, cursor, user, context=None):
        return 1

    def get_complete_name(self, cursor, user, ids, name, arg,
            context=None):
        res = self.name_get(cursor, user, ids, context)
        return dict(res)

    def name_get(self, cursor, user, ids, context=None):
        if not ids:
            return []
        categories = self.browse(cursor, user, ids, context=context)
        res = []
        for category in categories:
            if category.parent:
                name = category.parent.name+' / '+ category.name
            else:
                name = category.name
            res.append((category.id, name))
        return res

Category()
