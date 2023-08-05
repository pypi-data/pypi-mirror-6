exports.toolbar.on = (function() {
    /**
     * Updates toolbar buttons to reflect the current fullescreen mode.
     */
    function fullscreenUpdate() {
        var onEls = document.querySelectorAll(".toolbar > .fullscreen-on");
        var offEls = document.querySelectorAll(".toolbar > .fullscreen-off");
        if (document.fullscreenElement) {
        }
        else {
        }
    }

    return {
        fullscreenUpdate: fullscreenUpdate,

        fullscreenOn: function() {
            document.documentElement.requestFullscreen();
            fullscreenUpdate();
        },

        fullscreenOff: function() {
            document.documentElement.exitFullscreen();
            fullscreenUpdate();
        }};
})();
