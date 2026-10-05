package club.mulberry.game;

import android.os.Bundle;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;
import com.getcapacitor.BridgeActivity;

/** MULBERRY: полный экран без системных панелей, только альбомная ориентация (см. манифест). */
public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        WindowCompat.setDecorFitsSystemWindows(getWindow(), false);
        getWindow().getDecorView().setBackgroundColor(0xFF0D090B);
        getBridge().getWebView().setBackgroundColor(0xFF0D090B);
        // крупный шрифт в настройках телефона не должен ломать вёрстку игры
        getBridge().getWebView().getSettings().setTextZoom(100);
        // вырез камеры обрабатывает сам Capacitor (SystemBars): отдаёт его в CSS env(safe-area-inset-*), вёрстка их учитывает
        hideBars();
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) hideBars(); // после шторки уведомлений / возврата из Telegram панели снова прячем
    }

    private void hideBars() {
        WindowInsetsControllerCompat c = WindowCompat.getInsetsController(getWindow(), getWindow().getDecorView());
        c.hide(WindowInsetsCompat.Type.systemBars());
        c.setSystemBarsBehavior(WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
    }
}
