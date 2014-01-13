module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    // vars
    static_dir: './static/',

    // config
    less: {
        main: {
            options: {
                compress: true
            },
            src: ['<%= static_dir %>less/pressurenet.less'],
            dest: '<%= static_dir %>css/style.css'
        }
    },
    // TODO: Javascript
    concat: {},
    uglify: {},

    jshint: {
        gruntfile: ['Gruntfile.js']
    },

    clean: {
        css: {
            src: ['<%= less.main.dest %>']
        }
    },

    watch: {
        options: {
            livereload: true
        },
        gruntfile: {
            files: ['Grunfile.js'],
            tasks: ['jshint:gruntfile']
        },
        less: {
            files: ['<%= static_dir %>less/**/*.less'],
            tasks: ['clean:css', 'less']
        },
        templates: {
            files: ['templates/**/*.html']
        }
    }

  });

  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-jshint');

  // Default task.
  grunt.registerTask('default', ['build']);
  grunt.registerTask('build', ['clean', 'jshint', 'concat', 'uglify', 'less']);

};
