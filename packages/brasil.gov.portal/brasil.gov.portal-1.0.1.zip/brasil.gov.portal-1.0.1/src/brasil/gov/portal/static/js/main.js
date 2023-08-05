var PBrasil = {
    init: function(){
        this.main();
        this.addClassHtml();
        this.onclickBuscar();
        this.bugfixBase();
        this.carregaDestaques();
    },

    main: function() {

        // simulando click no botao do portlet header via mobile
        // author: deserto digital
        $('.portletNavigationTree .portletHeader').click(function () {
            $(this).toggleClass('ativo');
            $(this).next().slideToggle();
        });

        var menuTrigger = $(".menuTrigger");
        var navigationEl = $("#navigation");

        menuTrigger.click(function (e) {
            e.preventDefault();
            navigationEl.toggleClass("ativo");
        });

        var sectionTrigger = $(".mobile .portletNavigationTree dt a");
        sectionTrigger.append("<span></span>");


        sectionTrigger.click(function (e) {
            e.preventDefault();
            $(this).parent().parent().toggleClass("ativo");
        });
        $("ul li:last-child").addClass("last-item");

        var responsiveResize, root;

        root = typeof exports !== "undefined" && exports !== null ? exports : this;

        root.ResponsiveResize = function () {
            var _Singleton, _base;
            _Singleton = (function () {
                function _Singleton() {}

                _Singleton.prototype.perspectiva_anterior = '';
                _Singleton.prototype.scrollbar = false;

                _Singleton.prototype.resize = function () {
                    var perspectiva_atual;

                    if ($(window).width() <= 480) {
                        perspectiva_atual = 'mobile';
                    } else {
                        perspectiva_atual = 'desktop';
                    }

                    if (this.perspectiva_anterior !== perspectiva_atual) {
                        this.perspectiva_anterior = perspectiva_atual;

                        if (perspectiva_atual === 'mobile') {
                            $("body").addClass("mobile");
                        } else { // Desktop
                            $("body").removeClass("mobile");
                        }
                    }
                };

                return _Singleton;
            })();


            if ((_base = root.ResponsiveResize).instance == null) {
                _base.instance = new _Singleton();
            }
            return root.ResponsiveResize.instance;
        };

        var resize = function () {
            responsiveResize = new root.ResponsiveResize();
            responsiveResize.resize();
        }

        $(window).resize(function () {
            resize();
        });

        resize();

        $('.newsImageContainer .photo-icon').on('click', function(e) {
            e.preventDefault();
            $('#parent-fieldname-image').trigger('click');
        });

    },

    addClassHtml: function(){

        $("#portal-column-one div:first-child").addClass("first-item");

        /* Protection from the Content Manager */
        var firstNavigation = $("#portal-column-one .portletWrapper .portletNavigationTree")[0];
        if(firstNavigation){
            $(firstNavigation).addClass("first-item-nav");
        }

        if($('.link-externo').length > 0){
            $('.link-externo .collection-item:even').addClass ('even');
            $('.link-externo .collection-item:odd').addClass ('odd');
        }

    },

    onclickBuscar: function(){

        $('#link-buscar').click(function (e) {
            e.preventDefault();
            window.location.hash = '#portal-searchbox';
            $('.searchField').focus();
        });

    },

    /*
     * Bug fix para o bug de <base url=""> do Plone
     */
    bugfixBase: function(){

        if($("base").length > 0 && $(".userrole-anonymous").length > 0) {
            var aCurrentUrl = document.location.href.match(/(^[^#]*)/);

            $("base").attr("href", aCurrentUrl[1]);
        }
    },

    /*
     * Carrega capa /destaques no viewlet de destaques
     */
    carregaDestaques: function(){

        if ($('#featured-content').length > 0) {
            $('#featured-content').load(portal_url + '/destaques?ajax_load=1 #content > .row');
        }

    }
}

jQuery(document).ready(function ($) {
    "use strict";
    PBrasil.init();
});
