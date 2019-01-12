package com.kinuxer.punchrem.dao

import android.content.ContentValues
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.util.Log
import com.kinuxer.punchrem.utils.DateTime
import com.kinuxer.punchrem.utils.TextUtils
import java.time.DayOfWeek
import java.time.LocalDate
import java.time.LocalTime

class DBManager(context: Context) {
    private var db = DBOpenHelper(context).writableDatabase

    companion object {
        private val observers = arrayListOf<() -> Unit>()
        fun addObserver(observer: () -> Unit) {
            observers.add(observer)
        }

        fun onChange() {
            for (i in observers) {
                i()
            }
        }
    }

    fun queryByDate(date: LocalDate? = null): ArrayList<Array<String?>> {
        val cursor = if (date == null) db.query(DBOpenHelper.TABLE, null,
                null, null, null, null, "date desc")
        else db.query(DBOpenHelper.TABLE, null, "date>${DateTime.DateFormater.format(date)}",
                null, null, null, "date desc")
        Log.d(this.javaClass.simpleName, cursor.count.toString())
        val records = arrayListOf<Array<String?>>()
        while (cursor.moveToNext()) {
            val recordDate = cursor.getString(cursor.getColumnIndexOrThrow("date"))
            val recordInTime = cursor.getString(cursor.getColumnIndexOrThrow("in_time"))
            val recordOutTime = cursor.getString(cursor.getColumnIndexOrThrow("out_time"))
            val recordDayOfWeek = cursor.getString(cursor.getColumnIndexOrThrow("day_of_week"))
            records.add(arrayOf(recordDate, recordInTime, recordOutTime, recordDayOfWeek))
        }
        return records
    }

    fun insert(date: LocalDate, inTime: LocalTime?, outTime: LocalTime?, dayOfWeek: DayOfWeek, notifyNow: Boolean = true) {
        Log.d(this.javaClass.simpleName, "insert")
        val dateStr = DateTime.DateFormater.format(date)
        val inTimeStr = if (inTime != null) DateTime.TimeFormter.format(inTime) else null
        val outTimeStr = if (outTime != null) DateTime.TimeFormter.format(outTime) else null
        val dayOfWeekStr = DateTime.getDayOfWeek(dayOfWeek)

        val values = ContentValues()
        values.put("date", dateStr)
        values.put("in_time", inTimeStr)
        values.put("out_time", outTimeStr)
        values.put("day_of_week", dayOfWeekStr)

        if (-1L != db.insertWithOnConflict(DBOpenHelper.TABLE, null, values, SQLiteDatabase.CONFLICT_IGNORE)
                && notifyNow) {
            onChange()
        }
    }

    fun update(inTime: LocalTime?, outTime: LocalTime?, date: String) {
        Log.d(this.javaClass.simpleName, "update->$inTime, $outTime, $date")
        val values = ContentValues()
        if(inTime!=null) {
            values.put("in_time",DateTime.TimeFormter.format(inTime))
        }

        if(outTime!=null) {
            values.put("out_time",DateTime.TimeFormter.format(outTime))
        }

        db.update(DBOpenHelper.TABLE,values,
                "date == '$date'",null)
        onChange()
    }


    fun restoreFromCSV(list: List<String>) {
        for (line in list) {
            val fields = TextUtils.split(",", line)
            db.execSQL("insert or ignore into ${DBOpenHelper.TABLE} " +
                    "values('${fields[0]}','${fields[1]}','${fields[2]}','${fields[3]}')")
        }
        onChange()
    }

    fun clear(date: LocalDate? = null) {
        if (date == null) {
            db.execSQL("delete from ${DBOpenHelper.TABLE}")
        } else {
            db.execSQL("delete from ${DBOpenHelper.TABLE} where date < '${DateTime.DateFormater.format(date)}'")
        }
        onChange()
    }

    fun getCount(): Int {
        return db.query(DBOpenHelper.TABLE, null, null, null,
                null, null, null).count
    }
}