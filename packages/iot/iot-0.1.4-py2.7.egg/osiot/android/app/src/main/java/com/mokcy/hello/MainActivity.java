package com.mokcy.hello;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.Menu;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;


public class MainActivity extends Activity {
	TextView tv1;
	
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button aboutButton=(Button) findViewById(R.id.about_button);
        aboutButton.setOnClickListener(new View.OnClickListener(){	
			@Override
			public void onClick(View v) {
				// TODO Auto-generated method stub
				callAbout();
			}		
		});
        Button dataGetButton=(Button) findViewById(R.id.getdata_button);
        dataGetButton.setOnClickListener(new View.OnClickListener(){	
			@Override
			public void onClick(View v) {
				// TODO Auto-generated method stub
				getData();
			}
		});

    }


	@Override
    public boolean onCreateOptionsMenu(Menu menu) {   
        return super.onCreateOptionsMenu(menu);
    }
    
    public void getData(){
    	Intent startGet=new Intent(MainActivity.this,GetData.class);
    	startActivity(startGet);
    }
    
    public void callAbout(){
    	Intent start=new Intent(MainActivity.this,About.class);
    	startActivity(start);
    }

    public void syncData(){
	    AsyncHttpClient client=new AsyncHttpClient();
	    client.get("http://api.phodal.com/api/v1", new AsyncHttpResponseHandler(){
	    	@Override
	    	public void onSuccess(String response){
	    		System.out.println(response);
	    	}
	    });
    }
}
