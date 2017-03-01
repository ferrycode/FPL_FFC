'use strict';

angular.module('AngularFlask', ['angularFlaskServices', 'smart-table'])
	.config(['$routeProvider', '$locationProvider',
		function($routeProvider, $locationProvider) {
		$routeProvider
		.when('/', {
			templateUrl: '../static/partials/landing.html',
			controller: IndexController
		})
		.when('/tie', {
			templateUrl: '../static/partials/about.html',
			controller: TieController
		})
		.when('/post', {
			templateUrl: '../static/partials/post-list.html',
			controller: PostListController
		})
		.when('/scorecard', {
			templateUrl: '../static/partials/scoreboard.html',
			controller: ScoreBoardController
		})
		.when('/diff', {
			templateUrl: '../static/partials/diff.html',
			controller: DiffController
		})
		.when('/player-count', {
			templateUrl: '../static/partials/count.html',
			controller: PlayerCountController
		})
		/* Create a "/blog" route that takes the user to the same place as "/post" */
		.when('/blog', {
			templateUrl: '../static/partials/post-list.html',
			controller: PostListController
		})
		.otherwise({
			redirectTo: '/'
		})
		;

		$locationProvider.html5Mode(true);
	}])
;