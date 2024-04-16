(function(){

    function _dataApiHandler(event) {

        if (event.type === 'resize') {
            document.body.classList.remove('navbar-dropdown-open');
            document.querySelector('.navbar-dropdown').querySelector('.navbar-collapse').classList.remove('show');
            document.querySelector('.navbar-dropdown').classList.remove('opened');
            Array.from(document.querySelector('.navbar-dropdown').querySelectorAll('.navbar-toggler[aria-expanded="true"]')).forEach(el => {
                let target = el.querySelector(el.getAttribute('data-target'));
                if (target) {
                    target.classList.remove('in');
                    target.setAttribute('aria-expanded', 'false');
                    el.setAttribute('aria-expanded', 'false');
                }

            });
        }

        let scrollTop = document.documentElement.scrollTop;

        Array.from(document.querySelectorAll('.navbar-dropdown')).forEach(el => {

            if (!el.matches('.navbar-fixed-top')) return;

            if (el.matches('.transparent') && !el.classList.contains('opened')) {
                if (scrollTop > 0) {
                    el.classList.remove('bg-color');
                } else {
                    el.classList.add('bg-color');
                }
            }

            if (scrollTop > 0) {
                el.classList.add('navbar-short');
            } else {
                el.classList.remove('navbar-short');
            }

        });
    }


    var _timeout;
    var windowEvents = ['scroll', 'resize'];
    windowEvents.forEach(eventName => {
        document.addEventListener(eventName, event => {
            clearTimeout(_timeout);
                _timeout = setTimeout(function(){
                    _dataApiHandler(event);
                }, 10);
        });
    });


    let dropdownEvents = ['show.bs.collapse', 'hide.bs.collapse'];
    dropdownEvents.forEach(eventName => {
        document.addEventListener(eventName, () => {
            let dropDown = document.querySelector('.navbar-dropdown');
            if (dropDown) {
                if (eventName == 'show.bs.collapse') {
                    document.body.classList.add('navbar-dropdown-open');
                    dropDown.classList.add('opened');
                } else {
                    document.body.classList.remove('navbar-dropdown-open');
                    dropDown.classList.remove('opened');
                    window.dispatchEvent(new CustomEvent('scroll.bs.navbar-dropdown.data-api'));
                    dropDown.dispatchEvent(new CustomEvent('collapse.bs.navbar-dropdown'));
                }
            }
        });
    });

    document.addEventListener('collapse.bs.nav-dropdown', event => {
        let dropDown = event.relatedTarget.closest('.navbar-dropdown');
        if (dropDown) {
            let toggler = dropDown.querySelector('.navbar-toggler[aria-expanded="true"]');
            if (toggler) {
                toggler.dispatchEvent(new CustomEvent('click'));
            }
        }
    });
})();