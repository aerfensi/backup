package com.kinuxer.punchrem.dao

import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper

class DBOpenHelper(context: Context) : SQLiteOpenHelper(context, DB_NAME, null, VERSION) {

    companion object {
        const val DB_NAME = "data.db"
        const val VERSION = 1
        const val TABLE = "punch"
    }

    override fun onCreate(db: SQLiteDatabase?) {
        /*日期作为一整个字段存储，而不是将年、月、日分三个字段存储。
        原因是方便 sqlite 中对日期作比较，比如只查询 20180115 之后的数据，date>'20180115'*/
        val sql = "create TABLE if not exists $TABLE(date text primary key,in_time text,out_time text,day_of_week text)"
        db?.execSQL(sql)
    }

    override fun onUpgrade(db: SQLiteDatabase?, oldVersion: Int, newVersion: Int) {
        // TODO: To change body of created functions use File | Settings | File Templates.
    }

}