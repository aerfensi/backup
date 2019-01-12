package com.kinuxer.punchrem

import android.app.Activity
import android.app.AlertDialog
import android.app.Dialog
import android.content.DialogInterface
import android.support.v4.app.DialogFragment
import android.os.Bundle
import android.support.annotation.StringRes

class MessageDialog : DialogFragment(){

    companion object {
        const val TAG="MessageDialog"
        private const val MSG_KEY="message_key"
        private const val TITLE_KEY="title_key"
        fun newInstance(@StringRes message:Int,@StringRes title:Int=R.string.notification):MessageDialog{
            val dialog=MessageDialog()
            val args=Bundle()
            args.putInt(MSG_KEY,message)
            args.putInt(TITLE_KEY,title)
            dialog.arguments=args
            return dialog
        }
    }

    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        val builder=AlertDialog.Builder(context)
        builder.setMessage(arguments.getInt(MSG_KEY))
        builder.setTitle(arguments.getInt(TITLE_KEY))
        if(callback != null){
            builder.setPositiveButton(android.R.string.ok, {
                dialog,which -> callback?.invoke()
            })
        }
        builder.setNegativeButton(android.R.string.cancel, null)
        return builder.create()
    }

    var callback:(()->Unit)? = null
}