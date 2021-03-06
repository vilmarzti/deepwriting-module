import * as fs from 'fs';
import {request } from 'http';
import { RequestOptions } from 'https';

const { createSVGWindow } = require('svgdom')
const window = createSVGWindow()
const document = window.document
const port = 8001

const { SVG, registerWindow } = require('@svgdotjs/svg.js')
// register window and document
registerWindow(window, document)


// Interface for sending an object 
interface TextObject{
    wholeword_segments : "",
    word_ascii: string;
    word_stroke: WordStroke[];
}

interface WordStroke {
    type: string;
    x: number;
    y: number;
    ev: number;
    ts: any;
}

// step through paths and cut them into <num_step> pieces
let num_cuts = 50;
function cut_path_num_cuts(paths: any): any[][]{
    let cut_paths = [];
    for (let path of paths){
        let path_points = [];
        let path_step = path.length() / num_cuts;
        for(let i = 0; i < 100; i++){
            path_points.push(path.pointAt(path_step * i));
        }
        cut_paths.push(path_points);
    }
    return cut_paths;
}

// step through paths and cut them at even intervals
let step_distance = 3;
function cut_path_steps(paths: any): any[][]{
    let cut_paths = []
    for( let path of paths){
        let path_points: any[] = [];
        let index = 0;
        while(index * step_distance < path.length()){
            path_points.push(path.pointAt(index * step_distance));
            index++;
        }
        cut_paths.push(path_points);
    }

    return cut_paths;
}

// find all permutations of an array
function perm(xs: any[]) {
  let ret = [];

  for (let i = 0; i < xs.length; i = i + 1) {
    let rest: any = perm(xs.slice(0, i).concat(xs.slice(i + 1)));

    if(!rest.length) {
      ret.push([xs[i]])
    } else {
      for(let j = 0; j < rest.length; j = j + 1) {
        ret.push([xs[i]].concat(rest[j]))
      }
    }
  }
  return ret;
}

function compose_data_format(paths: any[]){
    // compose correct data format
    let text_object: TextObject = {
        wholeword_segments: "",
        word_ascii: "",
        word_stroke: []
    }
    for(let path of paths){
        for( let [index, point] of path.entries()){
            let type: string = "move";
            let ev: number = 0;

            if(index === 0){
                type = "start";
            }

            if(index === num_cuts - 1){
                type = "end";
                ev = 1;
            }

            let word_stroke: WordStroke = {
                type: type,
                x: point.x,
                y: point.y,
                ev: ev,
                ts: 0
            };

            text_object.word_stroke.push(word_stroke);
        }
    }

    return text_object;
}

function send_to_server(text_object: TextObject, interpretations: string[]){
    let options: RequestOptions = {
        hostname: "127.0.0.1",
        port: port,
        path: "/",
        method: "POST",
        headers: {
            'Content-Type': 'application/json;charset=UTF-8'
        },

    };

    let body_chunks: Uint8Array[] = [];
    const req = request(
       options,
       (res) =>{
           res.on('data', (chunk) =>{
               body_chunks.push(chunk);
           });
           res.on('end', () =>{
               let body = Buffer.concat(body_chunks).toString();
               interpretations.push(body);
               console.log(" " + JSON.parse(body).result);
           })
       }
    )

    req.on('error', (e)=>{
        console.log(e.message)
    });

    req.write(JSON.stringify(text_object));
    req.end();
}


// Read file if an arguments is given
if (process.argv.length === 3){
    let file_path = process.argv[2];

    // read file
    let svg_text = fs.readFileSync(file_path, {encoding: 'utf-8'});

    // read SVG
    let draw = SVG(document.documentElement);
    let store = draw.svg(svg_text);

    //let cut_paths: any[][] = cut_path_num_cuts(store.find("path"));
    let cut_paths: any[][] = cut_path_steps(store.find("path"));

    // find all permutations
    let perms = perm(cut_paths);

    // send to server for analysis
    for(let path of perms){
        let interpretations: string[]= []
        let text_object = compose_data_format(path);
        send_to_server(text_object, interpretations);
    }
}