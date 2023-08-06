var PyLocalSmtpApp = angular.module('PyLocalSmtpApp', [
    'inboxControllers',
    'inboxFilters',
    'igTruncate'
]);

PyLocalSmtpApp.config(function($interpolateProvider){
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});
