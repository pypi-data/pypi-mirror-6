module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    
    base_folder: '.',
    static_folder: '<%= base_folder %>/../static',
    build_folder: '<%= static_folder %>/build',

    template_folder: '<%= base_folder %>/template',
    
    js_folder: '<%= base_folder %>/js',
    js_build_folder: '<%= static_folder %>/javascripts',
    
    less_folder: '<%= base_folder %>/less',
    less_file: '/main.less',
    css_build_folder: '<%= static_folder %>/stylesheets',
    
    bootstrap: 'node_modules/twitter-bootstrap-3.0.0',
    
    pkg: grunt.file.readJSON('package.json'),
    
    
    less: {
      production: {
        options: {
          cleancss: true
        },
        files: {
          '<%= css_build_folder %>/main.css': ['<%= less_folder + less_file %>']
        }
      }  
    },
    
    
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
      },
      build: {
        src: [
          '<%= js_build_folder %>/app.js'
        ],
        dest: '<%= js_build_folder %>/app.js'
      }
    },
    
    jshint: {
      files: ['gruntfile.js', '<%= js_folder %>/app/*.js', '<%= js_folder %>/view/*.js'],
      options: {
        //laxcomma, because my commas are more awesome
        laxcomma: true,
        
        globals: {
          jQuery: true,
          console: true,
          module: true
        }
      }
    },
    
    removelogging: {
      dist: {
        src: "<%= js_build_folder %>/app.js",
        dest: "<%= js_build_folder %>/app.js"
      }
    },

    concat: {
      js: {
        src: [
          //'<%= js_folder %>/lib/jquery*',
          '<%= bootstrap %>/js/collapse.js',
//          '<%= bootstrap %>/js/button.js',
//          'node_modules/jquery-placeholder/jquery.placeholder.js',
          '<%= js_folder %>/lib/*.js',
          '<%= js_folder %>/app/*.js',
          '<%= js_folder %>/model/*.js',
          '<%= js_folder %>/view/*.js'
        ],
        dest: '<%= js_build_folder %>/main.js'
      },

      build: {
        options: {
//          banner: '<!DOCTYPE html> <html lang="nl"> ',
//          footer: '</html>',
        },
        files: {
          '<%= static_folder %>/page.html': ['<%= template_folder %>/startpage.html', '<%= template_folder %>/page.html', '<%= template_folder %>/endpage.html'],
          '<%= static_folder %>/search.html': ['<%= template_folder %>/startpage.html', '<%= template_folder %>/search.html', '<%= template_folder %>/endpage.html'],
          '<%= static_folder %>/homepage.html': ['<%= template_folder %>/startpage.html', '<%= template_folder %>/homepage.html', '<%= template_folder %>/endpage.html']
        }
      },


    },
    
    watch: {
      css: {
        files: ['<%= less_folder %>/**/*.less'],
        tasks: ['css']
      },
      js: {
        files: ['<%= js_folder %>/**/*.js'],
        tasks: ['jsdev']
      },
      template: {
        files: ['<%= template_folder %>/**/*.html'],
        tasks: ['build']
      }
    }
  
  //end initconfig  
  });

  grunt.loadNpmTasks('grunt-contrib-less');
  
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-remove-logging');

  grunt.loadNpmTasks('grunt-contrib-concat');
  
  grunt.loadNpmTasks('grunt-contrib-watch');
  
  // Default task(s).
  grunt.registerTask('default', ['js','css']);
  
  grunt.registerTask('js', ['jshint', 'concat:js', 'removelogging', 'uglify']);
  grunt.registerTask('jsdev', ['jshint', 'concat:js']);
  grunt.registerTask('css', ['less']);
  grunt.registerTask('build', ['concat:build']);
  
};