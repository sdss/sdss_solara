<template>
    <p style="display: none;"></p>
</template>

<script>
export default {
    props: {
    },
    data() {
        return {
            lastMessageType: '',
            postData: {}
        }
    },
    mounted() {
        window.addEventListener('message', this.handleMessage)
    },
    beforeUnmount() {
        window.removeEventListener('message', this.handleMessage)
    },
    methods: {
        handleMessage(event) {
            // event handler for postMessage
            if (event.data && event.data.type) {
                this.lastMessageType = event.data.type
                this.postData = event.data
                this.update(this.postData)
            }
        }
    }
}
</script>