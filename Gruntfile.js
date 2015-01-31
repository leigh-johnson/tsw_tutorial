module.exports = function( grunt ) {
    
  grunt.initConfig({
     watch: {
        options: {
          livereload: 1337
        },
        css: {
            files: [ 'view/public/css/*.css' ],
            tasks: [ 'default' ]
        },
        js: {
            files: [ 'view/public/js/*.js' ],
            tasks: [ 'default' ]
        }
      },
      sass: {                              // Task
        dist: {                            // Target
            options: {                       // Target options
              style: 'expanded'
            },
        files: {                         // Dictionary of files
        'view/public/css/style.css': 'view/public/scss/style.scss',       // 'destination': 'source'
         }
        }
      }
  });
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-sass');
  grunt.registerTask( 'default', ['watch'], ['sass']);
};