
/* Controllers */
/* ----------- */

var inboxControllers = angular.module('inboxControllers', []);

inboxControllers.controller('InboxCtrl', function ($scope, $http, $sce) {
    $http.get('/mail/').success(function(data) {
        $scope.mails = data.object_list;
        if($scope.mails.length > 0){
            $scope.readMail($scope.mails[0]);
        }
    });
    $scope.orderProp = 'sent_date';

    $scope.incomingMail = function(newmail){
        $scope.$apply(function() {
           $scope.mails.unshift(newmail);
       });
    }

    $scope.readMail = function(mail){
        $http.get('/mail/' + mail.id + "/").success(function(data){
            mail.read = true;
            $scope.currentMail = mail;
        });
    }

    $scope.readAll = function(mail){
        $http.post('/mail/all/read/').success(function(data){
            angular.forEach($scope.mails, function(mail){
                mail.read = true;
            });
        });
    }

    $scope.deleteAll = function(mail){
        if(confirm("Do you really want to permanently delete all messages ?")){
            $http.post('/mail/all/delete/').success(function(data){
                $scope.currentMail = null;
                $scope.mails = [];
            });
        }
        
    }

    $scope.deliberatelyTrustDangerousSnippet = function() {
        if($scope.currentMail){
            return $sce.trustAsHtml($scope.currentMail.body_html);
        }
    };

    /* Websockets */

    var conn = new SockJS('/inbox');
    conn.onopen = function() {
        conn.send();
    };
    conn.onmessage = function(e) {
        // recv += 1;
        $scope.incomingMail(e.data);
    };
});