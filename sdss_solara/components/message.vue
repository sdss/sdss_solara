<template>
    <p style="display: none;"></p>
</template>

<script>
export default {
    name: "Message",
    props: {
        outgoing: {type: Object, default: () => ({})}
    },
    data() {
        return {
            lastMessageType: '',
            parentOrigin: '*'
        }
    },
    mounted() {
        window.addEventListener('message', this.handleMessage)
    },
    beforeUnmount() {
        window.removeEventListener('message', this.handleMessage)
    },
    watch: {
        outgoing: function handler(newValue) {
            // watch for changes to the outgoing prop
            if (newValue && Object.keys(newValue).length > 0) {
                this.postMessage(newValue)
            }
        }
    },
    methods: {
        handleMessage(event) {
            // handle incoming message from the parent
            if (event.data && event.data.type) {
                this.lastMessageType = event.data.type

                // update parent origin
                if (event.origin) {
                    this.parentOrigin = event.origin
                }

                // call solara event handler
                // solara maps event_update to this.update
                // see https://solara.dev/documentation/api/utilities/component_vue#component_vue
                this.update(event.data)
            }
        },
        postMessage(message) {
            // post message back to the parent
            window.parent.postMessage(message, this.parentOrigin)
        },
    }
}
</script>