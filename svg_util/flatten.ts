import { SVG } from "@svgdotjs/svg.js";
import * as fs from 'fs';

// Read file if an arguments is given
if (process.argv.length === 3){
    let file_path = process.argv[2];
    // read file
    fs.readFile(file_path, {encoding: 'utf-8'}, (err, data) =>{
        if (err) throw err

        // create svg-element
        let draw = SVG();
        draw.svg(data);
        console.log(draw);
    });
}