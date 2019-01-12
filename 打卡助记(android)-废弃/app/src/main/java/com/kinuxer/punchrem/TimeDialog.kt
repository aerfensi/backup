package com.kinuxer.punchrem

import android.app.Dialog
import android.app.TimePickerDialog
import android.os.Bundle
import android.preference.PreferenceManager
import android.support.v4.app.DialogFragment
import android.widget.TimePicker
import com.kinuxer.punchrem.dao.DBManager
import com.kinuxer.punchrem.utils.DateTime
import java.time.LocalTime
import java.util.*

/**
 * 选择时间，并存储到指定SharedPreference中
 */

class TimeDialog: DialogFragment(), TimePickerDialog.OnTimeSetListener {
    companion object {
        // 该DialogFragment被show时需要传入的tag
        const val TAG="time picker"
        //数据存储的方式，数据库或者是SharedPreferences
        const val DEST="destination"
        const val DEST_SP="sharedpreferences"
        const val DEST_DB="SQLite"
        //数据的位置，SharedPreferences的key，或者是数据库表格中的主键
        const val KEY="key"
        //如果存入的是数据库，还需要指定列名
        const val COLUMN="column"
        fun newInstance(key:String, column:String?=null,dest:String=DEST_SP): TimeDialog {
            val fragment = TimeDialog()
            val args=Bundle()
            args.putString(KEY,key)
            args.putString(DEST,dest)
            if (column != null){
                args.putString(COLUMN,column)
            }
            fragment.arguments=args
            return fragment
        }
    }

    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        val calendar= Calendar.getInstance()
        val hour=calendar.get(Calendar.HOUR_OF_DAY)
        val minute=calendar.get(Calendar.MINUTE)

        return TimePickerDialog(activity, this, hour, minute, true)
    }
    override fun onTimeSet(view: TimePicker?, hourOfDay: Int, minute: Int) {
        if(arguments.getString(DEST) == DEST_SP) {
            val editor = PreferenceManager.getDefaultSharedPreferences(activity).edit()
            editor.putString(arguments.getString(KEY), DateTime.TimeFormter.format(LocalTime.of(hourOfDay,minute)))
            editor.apply()
        }else if(arguments.getString(DEST) == DEST_DB){
            val dbManager = DBManager(activity)
            if (arguments.getString(COLUMN) == "in_time"){
                dbManager.update(LocalTime.of(hourOfDay,minute),null,arguments.getString(KEY))
            }else if (arguments.getString(COLUMN) == "out_time"){
                dbManager.update(null,LocalTime.of(hourOfDay,minute),arguments.getString(KEY))
            }
        }
    }
}