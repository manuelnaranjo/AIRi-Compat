package com.googlecode.android_scripting.facade;

import android.app.Service;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.SharedPreferences.Editor;
import android.preference.PreferenceManager;

import com.googlecode.android_scripting.Constants;
import com.googlecode.android_scripting.MainThread;
import com.googlecode.android_scripting.jsonrpc.RpcReceiver;
import com.googlecode.android_scripting.rpc.Rpc;
import com.googlecode.android_scripting.rpc.RpcDefault;
import com.googlecode.android_scripting.rpc.RpcOptional;
import com.googlecode.android_scripting.rpc.RpcParameter;
import com.googlecode.android_scripting.bluetooth.BluetoothDiscoveryHelper;
import com.googlecode.android_scripting.bluetooth.BluetoothDiscoveryHelper.BluetoothDiscoveryListener;
import com.googlecode.android_scripting.facade.AndroidFacade;
import com.googlecode.android_scripting.facade.FacadeManager;
import com.hexad.bluezime.ImprovedBluetoothDevice;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/**
 * This is a test facade.
 *
 * @author Naranjo Manuel Francisco <manuel@aircable.net>
 */

public class TestFacade extends RpcReceiver {

  private Service mService;
  private AndroidFacade mAndroidFacade;
  private BluetoothAdapter mBluetoothAdapter;
  private BluetoothSocket mSocket;
  private BluetoothConnection mConnection;

  public TestFacade(FacadeManager manager) {
    super(manager);
    mService = manager.getService();
    mAndroidFacade = manager.getReceiver(AndroidFacade.class);
    mBluetoothAdapter = MainThread.run(manager.getService(), new Callable<BluetoothAdapter>() {
        @Override
        public BluetoothAdapter call() throws Exception {
          return BluetoothAdapter.getDefaultAdapter();
        }
      });
  }

  @Rpc(description = "Echo back what it gets")
  public String testEcho(
      @RpcParameter(name = "msg") String msg
    ) {
    return msg;
  }

  @Override
  public void shutdown() {
	  myBluetoothDisconnect();
  }
  
  @Rpc(description = "Do a Bluetooth scan")
  public JSONArray bluetoothScan() throws InterruptedException{
	  DiscoveryListener listener = new DiscoveryListener();
	  BluetoothDiscoveryHelper helper = new BluetoothDiscoveryHelper(
			  this.mService, listener);
	  helper.startDiscovery();
	  listener.mLatch.await(30, TimeUnit.SECONDS);
	  helper.cancel(); 
	  // needed because there's a bug in the BluetoothDiscoveryHelper
	  // that's leaking it own broadcast receiver on successful scan
	  // complete
	  return listener.results;
  }
  
  @Rpc(description = "Disconnect any pending Bluetooth connection")
  public boolean myBluetoothDisconnect(){
	  if (mSocket == null)
		  return false;
	  mConnection.stop();
	  mSocket = null;
	  return true;
  }
  
  @Rpc(description="Do an RFcomm Bluetooth connection, igoring service resolving")
  public boolean myBluetoothConnectRfcomm(
		  @RpcParameter(name="address") String address, 
		  @RpcParameter(name="channel") Integer channel
		  ) throws Exception{
	  BluetoothDevice mDevice = mBluetoothAdapter.getRemoteDevice(address);
	  ImprovedBluetoothDevice mIDevice = new ImprovedBluetoothDevice(mDevice);
	  mSocket = mIDevice.createRfcommSocket(channel);
	  mSocket.connect();
	  mConnection = new BluetoothConnection(mSocket);
	  return true;
  }
  
  @Rpc(description="Do an L2CAP Bluetooth Connection")
  public boolean myBluetoothConnectL2CAP(
		  @RpcParameter(name="address") String address,
		  @RpcParameter(name="channel") Integer channel 
		  ) throws Exception{
	  BluetoothDevice mDevice = mBluetoothAdapter.getRemoteDevice(address);
	  ImprovedBluetoothDevice mIDevice = new ImprovedBluetoothDevice(mDevice);
	  mSocket = mIDevice.createL2CAPSocket(channel);
	  mConnection = new BluetoothConnection(mSocket);
	  return true;
  }
  
  @Rpc(description="Read from Bluetooth Connection")
  public String myBluetoothRead() throws IOException{
	  return mConnection.readLine();
  }
  
  private class DiscoveryListener implements BluetoothDiscoveryListener{
	JSONArray results;
	CountDownLatch mLatch;
	
	public DiscoveryListener(){
		mLatch = new CountDownLatch(1);
		results = new JSONArray();
	}
	
	private void addDevice(String name, String address, boolean bond){
		try {
			JSONObject res = new JSONObject();
			res.put("name", name);
			res.put("address", address);
			res.put("bonded", bond);
			results.put(res);
		} catch (JSONException e) {
			e.printStackTrace();
		}		
		
	}
		  
	@Override
	public void addBondedDevice(String name, String address) {
		this.addDevice(name, address, true);
	}
	
	@Override
	public void addDevice(String name, String address) {
		this.addDevice(name, address, false);
	}
	
	@Override
	public void scanDone() {
		this.mLatch.countDown();
	}
  }
}
