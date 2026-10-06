package club.mulberry.game;

import android.app.Activity;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.ActivityInfo;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/**
 * Ориентация экрана из настроек игры: "auto" | "portrait" | "landscape".
 * Выбор хранится в SharedPreferences и применяется в MainActivity.onCreate ещё до загрузки WebView.
 * auto — как в системе (учитывает блокировку поворота), portrait/landscape — с переворотом на 180° по датчику.
 */
@CapacitorPlugin(name = "Orientation")
public class OrientationPlugin extends Plugin {

    static final String PREFS = "mb_settings";
    static final String KEY = "orientation";

    static int toActivityInfo(String mode) {
        if ("portrait".equals(mode)) return ActivityInfo.SCREEN_ORIENTATION_USER_PORTRAIT;
        if ("landscape".equals(mode)) return ActivityInfo.SCREEN_ORIENTATION_USER_LANDSCAPE;
        return ActivityInfo.SCREEN_ORIENTATION_FULL_USER;
    }

    static String saved(Context ctx) {
        return ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getString(KEY, "auto");
    }

    static void apply(Activity activity, String mode) {
        activity.setRequestedOrientation(toActivityInfo(mode));
    }

    @PluginMethod
    public void set(PluginCall call) {
        String mode = call.getString("mode", "auto");
        if (!"portrait".equals(mode) && !"landscape".equals(mode)) mode = "auto";
        SharedPreferences.Editor ed = getContext().getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit();
        ed.putString(KEY, mode).apply();
        final String m = mode;
        getActivity().runOnUiThread(() -> apply(getActivity(), m));
        JSObject ret = new JSObject();
        ret.put("mode", mode);
        call.resolve(ret);
    }

    @PluginMethod
    public void get(PluginCall call) {
        JSObject ret = new JSObject();
        ret.put("mode", saved(getContext()));
        call.resolve(ret);
    }
}
