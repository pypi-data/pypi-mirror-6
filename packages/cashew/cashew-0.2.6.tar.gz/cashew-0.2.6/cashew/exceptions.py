class CashewException(Exception):
    pass

class InternalCashewException(CashewException):
    pass

class UserFeedback(CashewException):
    pass

class InactivePlugin(UserFeedback):
    def __init__(self, plugin_instance_or_alias):
        if isinstance(plugin_instance_or_alias, basestring):
            self.alias = plugin_instance_or_alias
        else:
            self.alias = plugin_instance_or_alias.alias

    def __str__(self):
        return "%s is inactive. Some additional software might need to be installed." % (self.alias)

class NoPlugin(UserFeedback):
    pass
