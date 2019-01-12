package com.kinuxer.punchrem.dao

import android.content.Context
import android.support.test.InstrumentationRegistry
import android.util.Log
import org.junit.After
import org.junit.Before
import org.junit.Test
import java.time.LocalDate
import java.time.LocalTime

class DBManagerTest {

    private lateinit var appContext: Context
    private lateinit var manager:DBManager

    @Before
    fun createDB(){
        appContext= InstrumentationRegistry.getTargetContext()
        manager= DBManager(appContext)
    }

    @Test
    fun insert(){
        val date=LocalDate.of(2018,1,1)
        val inTime=LocalTime.of(8,0)
        val outTime=LocalTime.of(17,30)
        for(i in 0..30){
            val tmp=date.plusDays(i.toLong())
            manager.insert(tmp, inTime,outTime,tmp.dayOfWeek,false)
        }
    }

    @Test
    fun queryByDate() {
        for(e in manager.queryByDate()){
            Log.d(this.javaClass.simpleName,e.contentToString())
        }

        for(e in manager.queryByDate(LocalDate.of(2018,1,15))){
            Log.d(this.javaClass.simpleName,e.contentToString())
        }
    }

    @Test
    fun clear(){
        manager.clear()
        assert(manager.getCount() == 0)
    }

    @After
    fun onFinish(){
    }
}