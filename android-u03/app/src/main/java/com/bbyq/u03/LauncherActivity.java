package com.bbyq.u03;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;

/** Exported LAUNCHER which intentionally ignores all caller-supplied extras. */
public final class LauncherActivity extends Activity {
    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // Never copy extras, data, flags or nested Intents from an external app.
        Intent internal=new Intent(this,IntegratedActivity.class);
        internal.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP|Intent.FLAG_ACTIVITY_SINGLE_TOP);
        startActivity(internal);
        finish();
    }
}
