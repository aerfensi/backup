package com.kinuxer.punchrem.utils

object TextUtils {
    fun join(delimiter:String,iterable:Iterator<Any?>) : String {
        val seq=StringBuilder()
        for(i in iterable){
            seq.append(i.toString(),delimiter)
        }
        seq.delete(seq.length - delimiter.length, seq.length)
        return seq.toString()
    }

    //csv文件相关
    fun split(delimiter:String,record:String) : List<String> {
        val list=record.split(',')
        val fields= mutableListOf<String?>()
        for (i in list){
            if(i == "null"){
                fields.add(null)
            }else{
                fields.add(i)
            }
        }
        return list.toList()
    }
}