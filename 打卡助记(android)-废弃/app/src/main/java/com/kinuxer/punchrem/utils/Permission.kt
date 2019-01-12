package com.kinuxer.punchrem.utils

import android.app.Activity
import android.content.Context
import android.content.pm.PackageManager
import android.support.v4.app.ActivityCompat
import android.support.v4.app.Fragment

object Permission {
    fun check(context: Context,permissions:ArrayList<String>):ArrayList<String>{
        val iterator = permissions.iterator()
        while(iterator.hasNext()){
            if (ActivityCompat.checkSelfPermission(context,iterator.next())
            == PackageManager.PERMISSION_GRANTED){
                iterator.remove()
            }
        }
        return permissions
    }

    fun request(activity: Activity,permissions:ArrayList<String>,code:Int){
        ActivityCompat.requestPermissions(activity, permissions.toArray(emptyArray<String>()),code)
    }

    fun request(fragment: Fragment,permissions:ArrayList<String>,code:Int){
        fragment.requestPermissions(permissions.toArray(emptyArray<String>()),code)
    }
}