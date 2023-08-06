
/* Filters */
/* ------- */
angular.module('inboxFilters', []).filter('is_read_css_class', function() {
    return function(input) {
        return input ? '' : 'email-item-unread';
    };
});
