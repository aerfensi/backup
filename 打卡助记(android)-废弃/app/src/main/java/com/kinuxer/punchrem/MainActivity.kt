package com.kinuxer.punchrem

import android.support.v4.app.FragmentTransaction
import android.os.AsyncTask
import android.os.Bundle
import android.support.v4.app.FragmentManager
import android.support.v7.app.AppCompatActivity
import android.util.Log
import android.view.*
import android.widget.AbsListView
import android.widget.BaseAdapter
import android.widget.ListView
import android.widget.TextView
import com.kinuxer.punchrem.dao.DBManager
import com.kinuxer.punchrem.utils.DateTime
import java.time.LocalDate
import java.time.LocalTime

class MainActivity : AppCompatActivity(), FragmentManager.OnBackStackChangedListener,
        AbsListView.OnScrollListener {

    private lateinit var listView: ListView
    private lateinit var adapter: RecordsAdapter
    private lateinit var defaultTitle:String
    private lateinit var dbManager:DBManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        defaultTitle=resources.getString(R.string.app_name)

        dbManager = DBManager(this)
        val today = LocalDate.now()
        WorkDayTask({
            dbManager.insert(today, null, null, today.dayOfWeek)
        }).execute(today.toString())

        supportFragmentManager.addOnBackStackChangedListener(this)
        listView = findViewById(R.id.list)
        adapter = RecordsAdapter(layoutInflater)
        listView.adapter = adapter
        listView.setOnScrollListener(this)
    }

    override fun onCreateOptionsMenu(menu: Menu?): Boolean {
        menuInflater.inflate(R.menu.main, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem?): Boolean {
        when (item?.itemId) {
            R.id.setting -> {
                if (supportFragmentManager.findFragmentByTag(SettingsFragment.TAG) == null) {
                    Log.d(this::class.java.simpleName, "add SettingsFragment fragment")
                    supportFragmentManager.beginTransaction()
                            .setTransition(FragmentTransaction.TRANSIT_FRAGMENT_OPEN)
                            .add(R.id.content, SettingsFragment.newInstance(), SettingsFragment.TAG)
                            .addToBackStack(null)
                            .commit()
                }
            }
        }
        return true
    }

    override fun onBackStackChanged() {
        Log.d(this.javaClass.simpleName, "onBackStackChanged")
        if (supportFragmentManager.backStackEntryCount == 0) {
            supportActionBar?.title = defaultTitle
        }
    }

    override fun onScroll(view: AbsListView?, firstVisibleItem: Int, visibleItemCount: Int, totalItemCount: Int) {
        if(view?.adapter?.count == 0){
            defaultTitle=resources.getString(R.string.app_name)
            return
        }

        val record = view?.getItemAtPosition(firstVisibleItem) as Array<String?>
        val date=record[0]?.split('-')
        val title="${date!![0]} ${date[1]}"
        if(supportActionBar?.title != title){
            supportActionBar?.title=title
            defaultTitle=title
        }
    }

    override fun onScrollStateChanged(view: AbsListView?, scrollState: Int) {
        
    }

    private inner class RecordsAdapter(val inflater: LayoutInflater)
        : BaseAdapter(),View.OnClickListener,View.OnLongClickListener {


        private var records=dbManager.queryByDate()

        init {
            DBManager.addObserver {
                records = dbManager.queryByDate()
                notifyDataSetChanged()
                Log.d(this.javaClass.simpleName, "notifyDataSetChanged")
            }
        }

        override fun getItem(position: Int): Array<String?> {
            return records[position]
        }

        override fun getItemId(position: Int): Long {
            return position.toLong()
        }

        override fun getCount(): Int {
            return records.size
        }

        override fun getView(position: Int, convertView: View?, parent: ViewGroup?): View {
            val viewHolder: ViewHolder
            val itemView: View
            val itemDate = getItem(position)
            if (convertView == null) {
                itemView = inflater.inflate(R.layout.record, null)
                val dayOfMonth = itemView.findViewById<TextView>(R.id.day_of_month)
                val dayOfWeek = itemView.findViewById<TextView>(R.id.day_of_week)
                val inTime = itemView.findViewById<TextView>(R.id.in_time)
                val outTime = itemView.findViewById<TextView>(R.id.out_time)
                viewHolder = ViewHolder(dayOfMonth, dayOfWeek, inTime, outTime)
                itemView.tag = viewHolder

                val punchIn=itemView.findViewById<View>(R.id.punch_in)
                punchIn.setOnClickListener(this)
                punchIn.setOnLongClickListener(this)
                punchIn.tag=TimeTag(inTime,-1)

                val punchOut=itemView.findViewById<View>(R.id.punch_out)
                punchOut.setOnClickListener(this)
                punchOut.setOnLongClickListener(this)
                punchOut.tag=TimeTag(outTime,-1)
            } else {
                itemView = convertView
                viewHolder = convertView.tag as ViewHolder
            }
            val date = itemDate[0]?.split('-')
            viewHolder.dayOfMonth.text = date!![2]
            viewHolder.dayOfWeek.text = itemDate[3]
            viewHolder.inTime.text = itemDate[1]
            viewHolder.outTime.text = itemDate[2]
            (itemView.findViewById<View>(R.id.punch_in).tag as TimeTag).position=position
            (itemView.findViewById<View>(R.id.punch_out).tag as TimeTag).position=position
            return itemView
        }

        override fun onClick(v: View?) {
            Log.d(this.javaClass.simpleName, "onClick")
            val tag = v?.tag as TimeTag
            if (tag.position == 0){
                setTime(v.id,tag)
            }
        }

        override fun onLongClick(v: View?): Boolean {
            Log.d(this.javaClass.simpleName, "onLongClick")

            val column = when {
                v?.id == R.id.punch_in -> "in_time"
                v?.id == R.id.punch_out -> "out_time"
                else -> return false
            }
            val tag = v.tag as TimeTag

            TimeDialog.newInstance(records[tag.position][0]!!,
                    column,TimeDialog.DEST_DB).show(supportFragmentManager,TimeDialog.TAG)
            return true
        }

        private fun setTime(id:Int,tag: TimeTag, force:Boolean=false){
            Log.d(this.javaClass.simpleName,"setTime")
            val now=LocalTime.now()
            if (id == R.id.punch_in){
                val start = LocalTime.of(8,0,0)
                val end = LocalTime.of(9,0,0)
                if ((tag.textView.text.isBlank() && now.isAfter(start) && now.isBefore(end)) || force){
                    dbManager.update(now,null, records[tag.position][0]!!)
                    Log.d(this.javaClass.simpleName,"setTime->update in time")
                }
            }else if(id == R.id.punch_out){
                val start = LocalTime.of(17,30,0)
                val end = LocalTime.of(21,0,0)
                if ((tag.textView.text.isBlank() && now.isAfter(start) && now.isBefore(end)) || force){
                    dbManager.update(null,now,records[tag.position][0]!!)
                    Log.d(this.javaClass.simpleName,"setTime->update out time")
                }
            }
        }

    }

    private data class ViewHolder(val dayOfMonth: TextView, val dayOfWeek: TextView,
                                  val inTime: TextView, val outTime: TextView)

    private data class TimeTag(val textView:TextView, var position: Int)

    private inner class WorkDayTask(val callback:()->Unit): AsyncTask<String, Unit, Boolean>() {

        override fun doInBackground(vararg params: String?): Boolean {
            return DateTime.isWorkDay(this@MainActivity, params[0] as String)
        }

        override fun onPostExecute(result: Boolean?) {
            super.onPostExecute(result)
            if(result as Boolean){
                callback()
            }
        }
    }
}
