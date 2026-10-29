import logging

from ipyvue.VueTemplateWidget import Events

logger = logging.getLogger("ipyvue_event_guard")


def install():
    """ipyvue patch"""
    if getattr(Events, "_unguarded_handle_event", None) is not None:
        return True  # already installed
    original = Events._handle_event

    def _handle_event(self, widget, content, buffers):
        if not isinstance(content, dict) or not isinstance(
            event := content.get("event"), str
        ):
            logger.error(
                "ipyvue_event_guard: dropped message for %s: %.4000r",
                type(self).__name__,
                content,
            )
            return
        original(
            self, widget, {"event": event, "data": content.get("data", {})}, buffers
        )

    Events._unguarded_handle_event = original
    Events._handle_event = _handle_event
    return True


install()
