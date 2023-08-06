"""A wrapper around PyChef to deal with configuration"""

from __future__ import absolute_import

import chef


class FlaskChefAPI(chef.ChefAPI):
    @classmethod
    def configure(cls, app, set_default=False):
        keys = ('CHEF_URL', 'CHEF_KEY', 'CHEF_CLIENT')
        args = (app.config[k] for k in keys)
        chef = cls(*args) if all(args) else cls.autoconfigure()

        if set_default:
            chef.set_default()

        return chef
