package com.kinuxer.punchrem

import org.junit.Test

import org.junit.Assert.*
import java.time.LocalDate
import java.time.LocalTime
import java.time.format.DateTimeFormatter
import java.util.*

/**
 * Example local unit test, which will execute on the development machine (host).
 *
 * See [testing documentation](http://d.android.com/tools/testing).
 */
class ExampleUnitTest {
    @Test
    fun addition_isCorrect() {
        assertEquals(4, 2 + 2)
    }

    @Test
    fun dateTime(){
        val formater=DateTimeFormatter.ofPattern("HH:mm")
    }

    @Test
    fun dataType(){

    }
}
