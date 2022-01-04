from logging import LoggerAdapter


class ExtensionLoggerAdapter(LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs['extra'] = extra

        if 'id' in extra:
            msg = f"{extra.get('id')} {msg}"

        return msg, kwargs
