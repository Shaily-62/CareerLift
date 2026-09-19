const mongoose = require("mongoose");

/**
 * - job description schema :string
 * - resume text:string
 * - self desc:string
 * 
 * - matchScore: number  ats score
 * ai
 * - technical question     : [{
 *                       questions:""
                        intention:""
                       answer:""   
                       }]     

 * - behavivoral question   : [{
 *                       questions:""
                        intention:""
                       answer:""   
                       }]     

 * - skill gaps  : [{
                       skill:""
                       severity:{
                       type:"string"
                       enum:["low","med","high"]
                       }
              }]

 * - preparation plan   : [{
              day:number,
              focus:String
              tasks:[string]
            }]    
 */


const interviewReportSchema = new mongoose.Schema({

})