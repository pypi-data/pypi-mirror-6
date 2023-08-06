define('app/views/user_menu', ['app/views/templated','ember'],
    /**
     *  User Menu View
     *
     *  @returns Class
     */
    function(TemplatedView) {
        return TemplatedView.extend({

            /**
             *  Properties
             */

            isNotCore: !IS_CORE,
            accountUrl: URL_PREFIX + '/account',
            //TODO: change the logo_splash.png to user.png
            gravatarURL: EMAIL && ('https://www.gravatar.com/avatar/' + md5(EMAIL) + '?d=' +
                  encodeURIComponent('https://mist.io/resources/images/user.png') +'&s=36'),


            /**
             * 
             *  Actions
             * 
             */

            actions: {

                meClicked: function(){
                    $('#user-menu-popup').popup('open');
                },

                loginClicked: function() {
                    $('#user-menu-popup').popup('close');
                    Ember.run.later(function() {
                        Mist.loginController.open();
                    }, 300);
                },

                logoutClicked: function() {
                    Mist.loginController.logout();
                }
            }
        });
    }
);
