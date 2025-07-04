const { resolve } = require("path");
const { src, watch, dest } = require("gulp");
const if_ = require("gulp-if");
const sass = require('gulp-sass')(require('sass'));
const sourcemaps = require("gulp-sourcemaps");
const with_sourcemaps = () => !!process.env.DEBUG

const themeDir = resolve("ckanext/ap_main/assets/scss");
const assetsDir = resolve("ckanext/ap_main/assets");

const build = () => {
    return src(resolve(themeDir, "admin_panel.scss"))
        .pipe(if_(with_sourcemaps(), sourcemaps.init()))
        .pipe(sass({ outputStyle: !!process.env.DEBUG ? 'expanded' : 'compressed' }).on('error', sass.logError))
        .pipe(if_(with_sourcemaps(), sourcemaps.write()))
        .pipe(dest(resolve(assetsDir, "css")))
}


const watchSource = () => {
    watch(
        themeDir + "/**/*.scss",
        { ignoreInitial: false },
        build
    )
}


exports.build = build;
exports.watch = watchSource;
