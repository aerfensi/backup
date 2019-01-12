package com.kinuxer.punchrem.utils

import android.content.ComponentCallbacks
import android.content.Context
import android.content.pm.PackageManager
import android.icu.text.DateFormat
import android.preference.PreferenceManager
import android.util.Log
import android.widget.Toast
import com.kinuxer.punchrem.R
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONObject
import java.time.DayOfWeek
import java.time.LocalDate
import java.time.format.DateTimeFormatter

object DateTime {

    // 比如2018年一月和二月 http://www.easybots.cn/api/holiday.php?m=201801,201802
    // 返回的数据中 1 为休息日，2 为节假日
    private const val BASE_HOLIDAY_URL="http://www.easybots.cn/api/holiday.php?m="
    val TimeFormter=DateTimeFormatter.ofPattern("HH:mm")
    val DateFormater=DateTimeFormatter.ISO_LOCAL_DATE

    fun getStartDate(): LocalDate {
        return LocalDate.now().minusWeeks(4)
    }

    fun getDayOfWeek(day:DayOfWeek):String{
        return when(day){
            DayOfWeek.MONDAY -> "一"
            DayOfWeek.TUESDAY -> "二"
            DayOfWeek.WEDNESDAY -> "三"
            DayOfWeek.THURSDAY -> "四"
            DayOfWeek.FRIDAY -> "五"
            DayOfWeek.SATURDAY -> "六"
            DayOfWeek.SUNDAY -> "日"
        }
    }

    //date 格式为 xxxx-xx-xx
    fun isWorkDay(context:Context,date:String):Boolean{
        val year=date.split('-')[0]
        val date=date.replace("-","")
        val sp=PreferenceManager.getDefaultSharedPreferences(context)
        var holidays=sp.getStringSet(year,null)
        if(holidays == null){
            try {
                holidays=getHoliday(year)
            }catch (e:Exception){
                e.printStackTrace()
                Toast.makeText(context, R.string.holiday_err,Toast.LENGTH_SHORT).show()
                return true
            }
            val editor=sp.edit()
            editor.putStringSet(year,holidays)
            editor.apply()
        }
        if (holidays.contains(date)){
            return false
        }
        return true
    }

    private fun getHoliday(year:String):Set<String>{
        val client = OkHttpClient()
        val request = Request.Builder().url(getHolidayUrl(year)).get().build()
        val response = client.newCall(request).execute()
        if(response.isSuccessful){
            val body=response.body()!!.string()
            Log.d(this.javaClass.simpleName,"getHoliday->response body = $body")
            return parseHolidayStr(body)
        }else{
            throw Exception("没有获取到节假日数据")
        }
    }

    private fun getHolidayUrl(year:String):String{
        val builder = StringBuilder(BASE_HOLIDAY_URL)
        for(i in 1..12){
            builder.append(String.format("$year%02d,",i))
        }
        builder.deleteCharAt(builder.length-1)
        val url=builder.toString()
        Log.d(this.javaClass.simpleName,"getHolidayUrl->url = $url")
        return url
    }

    private fun parseHolidayStr(data:String):Set<String>{
        val holiday= hashSetOf<String>()
        val yearJson=JSONObject(data)
        val monthKeys=yearJson.keys()
        while (monthKeys.hasNext()){
            val month=monthKeys.next()
            val monthJson= yearJson.getJSONObject(month.toString())
            val dayKeys=monthJson.keys()
            while (dayKeys.hasNext()){
                val day=dayKeys.next()
                holiday.add("$month$day")
            }
        }
        return holiday.toSet()
    }
}