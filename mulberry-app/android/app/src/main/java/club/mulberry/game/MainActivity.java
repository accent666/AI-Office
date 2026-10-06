package club.mulberry.game;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(OrientationPlugin.class);
        // сохранённая ориентация — до показа WebView, чтобы экран не «прыгал» при запуске
        OrientationPlugin.apply(this, OrientationPlugin.saved(this));
        super.onCreate(savedInstanceState);
    }
}
