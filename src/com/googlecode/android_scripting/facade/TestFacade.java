package net.aircable.airicompat;

import android.app.Service;
import android.content.SharedPreferences;
import android.content.SharedPreferences.Editor;
import android.preference.PreferenceManager;

import com.googlecode.android_scripting.jsonrpc.RpcReceiver;
import com.googlecode.android_scripting.rpc.Rpc;
import com.googlecode.android_scripting.rpc.RpcOptional;
import com.googlecode.android_scripting.rpc.RpcParameter;
import com.googlecode.android_scripting.facade.FacadeManager;

import java.io.IOException;
import java.util.Map;

/**
 * This is a test facade.
 *
 * @author Naranjo Manuel Francisco <manuel@aircable.net>
 */

public class TestFacade extends RpcReceiver {

  private Service mService;

  public TestFacade(FacadeManager manager) {
    super(manager);
    mService = manager.getService();
  }

  @Rpc(description = "Echo back what it gets")
  public String testEcho(
      @RpcParameter(name = "msg") String msg
    ) {
    return msg;
  }

  @Override
  public void shutdown() {
  }
}
