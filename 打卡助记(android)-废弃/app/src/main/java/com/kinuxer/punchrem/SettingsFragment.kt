package com.kinuxer.punchrem


import android.Manifest
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.os.Bundle
import android.os.Environment
import android.preference.PreferenceManager
import android.support.v4.app.Fragment
import android.support.v7.app.AppCompatActivity
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import com.kinuxer.punchrem.dao.DBManager
import com.kinuxer.punchrem.utils.DateTime
import com.kinuxer.punchrem.utils.Permission
import com.kinuxer.punchrem.utils.TextUtils
import java.io.File
import java.io.PrintWriter
import java.util.*

class SettingsFragment : Fragment(), View.OnClickListener, CompoundButton.OnCheckedChangeListener {

    companion object {
        fun newInstance(): SettingsFragment {
            return SettingsFragment()
        }

        const val TAG = "settings"
        //通知时间的key
        const val KEY_IN_TIME = "in time"
        const val KEY_OUT_TIME = "out time"
        //switch状态的key
        const val SWITCH_IN="switch in"
        const val SWITCH_OUT="switch out"
        //权限请求的code
        const val CODE_BACKUP = 0
        const val CODE_RESTORE = 1

        val PATH_BACKUP = Environment.getExternalStorageDirectory().path + File.separator + "Punchrem.csv"
    }

    private lateinit var inLayout: View
    private lateinit var outLayout: View
    private lateinit var inTimeTv: TextView
    private lateinit var outTimeTv: TextView
    private lateinit var inSwitch: Switch
    private lateinit var outSwitch: Switch
    private lateinit var inTitleTv: TextView
    private lateinit var outTitleTv: TextView

    private lateinit var clearBt: Button
    private lateinit var emptyBt: Button
    private lateinit var backupBt: Button
    private lateinit var restoreBt: Button

    override fun onCheckedChanged(buttonView: CompoundButton?, isChecked: Boolean) {
        when (buttonView?.id) {
            R.id.in_switch -> {
                inLayout.isEnabled = isChecked
                inTitleTv.setTextColor(resources.getColor(if (isChecked) android.R.color.black else R.color.unable, null))
                inTimeTv.setTextColor(resources.getColor(if (isChecked) android.R.color.black else R.color.unable, null))
                PreferenceManager
                        .getDefaultSharedPreferences(activity)
                        .edit()
                        .putBoolean(SWITCH_IN,isChecked)
                        .apply()
            }
            R.id.out_switch -> {
                outLayout.isEnabled = isChecked
                outTitleTv.setTextColor(resources.getColor(if (isChecked) android.R.color.black else R.color.unable, null))
                outTimeTv.setTextColor(resources.getColor(if (isChecked) android.R.color.black else R.color.unable, null))
                PreferenceManager
                        .getDefaultSharedPreferences(activity)
                        .edit()
                        .putBoolean(SWITCH_OUT,isChecked)
                        .apply()
            }

        }
    }

    override fun onClick(v: View?) {
        when (v?.id) {
            R.id.in_layout -> TimeDialog
                    .newInstance(KEY_IN_TIME)
                    .show(fragmentManager, TimeDialog.TAG)
            R.id.out_layout -> TimeDialog
                    .newInstance(KEY_OUT_TIME)
                    .show(fragmentManager, TimeDialog.TAG)
            R.id.clear -> {
                val dialog = MessageDialog.newInstance(R.string.clear_msg,R.string.clear)
                dialog.callback = {
                    val dbManager = DBManager(activity)
                    dbManager.clear(DateTime.getStartDate())
                }
                dialog.show(fragmentManager, MessageDialog.TAG)
            }
            R.id.empty -> {
                val dialog = MessageDialog.newInstance(R.string.empty_msg,R.string.empty)
                dialog.callback = {
                    val dbManager = DBManager(activity)
                    dbManager.clear()
                }
                dialog.show(fragmentManager, MessageDialog.TAG)
            }
            R.id.backup -> restoreOrBackup(R.id.backup)
            R.id.restore -> restoreOrBackup(R.id.restore)
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        var granted = true
        for (i in grantResults) {
            if (i != PackageManager.PERMISSION_GRANTED) {
                granted = false
            }
        }
        Log.d(this.javaClass.simpleName,"onRequestPermissionsResult -> granted == $granted, " +
                "requestCode == $requestCode")
        when (requestCode) {
            CODE_BACKUP, CODE_RESTORE -> if (granted) {
                if(requestCode == CODE_BACKUP) {
                    backup()
                }else if (requestCode == CODE_RESTORE){
                    restore()
                }
            } else {
                Toast.makeText(activity,R.string.storage_permission_denied,Toast.LENGTH_SHORT).show()
            }

        }
    }


    private fun backup() {
        val dbManager = DBManager(activity)
        val writer = PrintWriter(PATH_BACKUP, "UTF-8")
        for (i in dbManager.queryByDate()) {
            val line = TextUtils.join(",", i.iterator())
            Log.d(this.javaClass.simpleName, "write $line")
            writer.write(line+'\n')
            writer.flush()
        }
        writer.close()
        Toast.makeText(activity,R.string.backup_completed,Toast.LENGTH_SHORT).show()
    }

    private fun restore() {
        val file=File(PATH_BACKUP)
        if(!file.exists()){
            Toast.makeText(activity,R.string.no_backup,Toast.LENGTH_SHORT).show()
        }else {
            val scanner = Scanner(file)
            val dbManager = DBManager(activity)
            val list= mutableListOf<String>()
            while (scanner.hasNextLine()){
                list.add(scanner.nextLine())
            }
            dbManager.restoreFromCSV(list)
        }
        Toast.makeText(activity,R.string.restore_completed,Toast.LENGTH_SHORT).show()
    }

    private fun restoreOrBackup(id:Int){
        val list = arrayListOf(Manifest.permission.READ_EXTERNAL_STORAGE,
                Manifest.permission.WRITE_EXTERNAL_STORAGE)
        val permissions = Permission.check(activity, list)
        if (permissions.size == 0) {
            if(id == R.id.backup) {
                backup()
            }else if (id == R.id.restore){
                restore()
            }
        } else {
            if(id == R.id.backup) {
                Permission.request(this, permissions, CODE_BACKUP)
            }else if(id == R.id.restore){
                Permission.request(this, permissions, CODE_RESTORE)
            }
        }
    }


    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?,
                              savedInstanceState: Bundle?): View? {
        (activity as AppCompatActivity).supportActionBar?.title = resources.getString(R.string.setting)

        // Inflate the layout for this fragment
        val root = inflater.inflate(R.layout.fragment_settings, container, false)
        inLayout = root.findViewById(R.id.in_layout)
        inLayout.setOnClickListener(this)
        outLayout = root.findViewById(R.id.out_layout)
        outLayout.setOnClickListener(this)
        inTimeTv = root.findViewById(R.id.in_time)
        outTimeTv = root.findViewById(R.id.out_time)

        inSwitch = root.findViewById(R.id.in_switch)
        inSwitch.setOnCheckedChangeListener(this)
        outSwitch = root.findViewById(R.id.out_switch)
        outSwitch.setOnCheckedChangeListener(this)

        inLayout.isEnabled = inSwitch.isChecked
        outLayout.isEnabled = outSwitch.isChecked

        inTitleTv = root.findViewById(R.id.in_title)
        outTitleTv = root.findViewById(R.id.out_title)

        clearBt = root.findViewById(R.id.clear)
        clearBt.setOnClickListener(this)
        emptyBt = root.findViewById(R.id.empty)
        emptyBt.setOnClickListener(this)
        backupBt = root.findViewById(R.id.backup)
        backupBt.setOnClickListener(this)
        restoreBt = root.findViewById(R.id.restore)
        restoreBt.setOnClickListener(this)

        val sp=PreferenceManager.getDefaultSharedPreferences(activity)
        inTimeTv.text = sp.getString(KEY_IN_TIME, "")
        outTimeTv.text =sp.getString(KEY_OUT_TIME, "")
        inSwitch.isChecked=sp.getBoolean(SWITCH_IN, false)
        outSwitch.isChecked=sp.getBoolean(SWITCH_OUT, false)


        return root
    }

    private val spListener = SharedPreferences.OnSharedPreferenceChangeListener { sharedPreferences, key ->
        when (key) {
            KEY_IN_TIME -> inTimeTv.text = sharedPreferences.getString(key, "")
            KEY_OUT_TIME -> outTimeTv.text = sharedPreferences.getString(key, "")
        }
    }

    override fun onResume() {
        super.onResume()
        PreferenceManager.getDefaultSharedPreferences(activity)
                .registerOnSharedPreferenceChangeListener(spListener)
    }

    override fun onStop() {
        super.onStop()
        PreferenceManager.getDefaultSharedPreferences(activity)
                .unregisterOnSharedPreferenceChangeListener(spListener)
    }

}
