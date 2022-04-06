from logging import LoggerAdapter


class ExtensionLoggerAdapter(LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs['extra'] = extra

        if 'request_id' in extra:
            msg = f"{extra.get('request_id')} {msg}"

        return msg, kwargs
