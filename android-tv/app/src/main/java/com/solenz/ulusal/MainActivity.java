package com.solenz.ulusal;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.view.inputmethod.InputMethodManager;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.Toast;

import androidx.webkit.WebViewAssetLoader;

/** Android TV shell for the exact same Sinepad UI published at site/index.html. */
public final class MainActivity extends Activity {
    private static final String LOCAL_URL = "https://appassets.androidplatform.net/assets/index.html";
    private static final String DEFAULT_REMOTE_URL = "https://solenz-ulusal.onrender.com/";
    private static final String PREFS = "solenz_tv";
    private static final String SERVER_URL = "server_url";
    private FrameLayout root;
    private WebView webView;
    private WebChromeClient chromeClient;
    private View customView;
    private WebChromeClient.CustomViewCallback customCallback;
    private SharedPreferences prefs;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        immersive();
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        root = new FrameLayout(this);
        root.setBackgroundColor(Color.BLACK);
        setContentView(root);
        try {
            createWebView();
            openHome();
        } catch (RuntimeException ex) {
            new AlertDialog.Builder(this).setTitle("WebView bulunamadı")
                .setMessage("Bu televizyonda Android System WebView kurulmalı veya etkinleştirilmeli.\n" + ex.getClass().getSimpleName())
                .setPositiveButton("Kapat", (d, w) -> finish()).show();
        }
    }

    private void immersive() {
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
            View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
    }

    private void createWebView() {
        WebViewAssetLoader loader = new WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this)).build();
        webView = new WebView(this);
        webView.setBackgroundColor(Color.BLACK);
        webView.setFocusable(true);
        webView.setFocusableInTouchMode(true);
        root.addView(webView, new FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setMediaPlaybackRequiresUserGesture(false); // silent selected-channel preview
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setJavaScriptCanOpenWindowsAutomatically(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        webView.setWebViewClient(new WebViewClient() {
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                return loader.shouldInterceptRequest(request.getUrl());
            }
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                if (!request.isForMainFrame()) return false;
                Uri uri = request.getUrl();
                String selected = homeUrl();
                boolean local = "appassets.androidplatform.net".equals(uri.getHost()) && "https".equals(uri.getScheme());
                boolean configured = !LOCAL_URL.equals(selected) && "https".equals(uri.getScheme()) &&
                    uri.getHost() != null && uri.getHost().equals(Uri.parse(selected).getHost());
                return !(local || configured); // no unexpected top-level external navigation
            }
            @Override public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) fallbackIfRemoteError(request.getUrl());
            }
            @Override public void onReceivedHttpError(WebView view, WebResourceRequest request, WebResourceResponse response) {
                if (request.isForMainFrame() && response.getStatusCode() >= 400) fallbackIfRemoteError(request.getUrl());
            }
        });
        chromeClient = new WebChromeClient() {
            @Override public void onShowCustomView(View view, CustomViewCallback callback) {
                if (customView != null) { callback.onCustomViewHidden(); return; }
                customView = view;
                customCallback = callback;
                root.addView(view, new FrameLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
                immersive();
            }
            @Override public void onHideCustomView() {
                if (customView == null) return;
                root.removeView(customView);
                customView = null;
                if (customCallback != null) customCallback.onCustomViewHidden();
                customCallback = null;
                immersive();
            }
        };
        webView.setWebChromeClient(chromeClient);
        webView.requestFocus();
    }

    private String homeUrl() {
        String selected = prefs.getString(SERVER_URL, DEFAULT_REMOTE_URL);
        return selected.isEmpty() ? LOCAL_URL : selected;
    }

    private void openHome() {
        webView.loadUrl(homeUrl());
    }

    private void fallbackIfRemoteError(Uri failed) {
        String selected = homeUrl();
        if (LOCAL_URL.equals(selected) || failed.getHost() == null ||
            !failed.getHost().equals(Uri.parse(selected).getHost())) return;
        Toast.makeText(this, "Sunucuya erişilemiyor; gömülü sürüm açıldı", Toast.LENGTH_LONG).show();
        webView.loadUrl(LOCAL_URL);
    }

    // Android TV remote: MENU (or Settings) opens the server selector; D-pad goes to WebView.
    @Override public boolean dispatchKeyEvent(KeyEvent event) {
        int key = event.getKeyCode();
        if (key == KeyEvent.KEYCODE_MENU || key == KeyEvent.KEYCODE_SETTINGS) {
            if (event.getAction() == KeyEvent.ACTION_UP) showServerMenu();
            return true;
        }
        return super.dispatchKeyEvent(event);
    }

    private void showServerMenu() {
        new AlertDialog.Builder(this).setTitle("Solenz TV · Kaynak")
            .setItems(new String[]{"Render sitesini aç (varsayılan)", "Gömülü sürümü aç", "HTTPS adresini değiştir", "Sayfayı yenile"},
                (dialog, choice) -> {
                    if (choice == 0) {
                        prefs.edit().remove(SERVER_URL).apply();
                        openHome();
                    } else if (choice == 1) {
                        prefs.edit().putString(SERVER_URL, "").apply();
                        openHome();
                    } else if (choice == 2) {
                        showUrlInput();
                    } else {
                        webView.reload();
                    }
                }).show();
    }

    private void showUrlInput() {
        final EditText input = new EditText(this);
        input.setSingleLine(true);
        String configured = prefs.getString(SERVER_URL, DEFAULT_REMOTE_URL);
        input.setText(configured.isEmpty() ? DEFAULT_REMOTE_URL : configured);
        input.setSelectAllOnFocus(true);
        input.setInputType(android.text.InputType.TYPE_CLASS_TEXT | android.text.InputType.TYPE_TEXT_VARIATION_URI);
        new AlertDialog.Builder(this).setTitle("Render sitesi (HTTPS)")
            .setView(input)
            .setNegativeButton("Vazgeç", null)
            .setPositiveButton("Kaydet", (dialog, which) -> {
                String text = input.getText().toString().trim();
                Uri uri = Uri.parse(text);
                if (!"https".equals(uri.getScheme()) || uri.getHost() == null || uri.getUserInfo() != null) {
                    Toast.makeText(this, "Geçerli bir https:// adresi girin", Toast.LENGTH_LONG).show();
                    return;
                }
                prefs.edit().putString(SERVER_URL, text).apply();
                openHome();
            }).show();
    }

    @Override public void onBackPressed() {
        if (customView != null) {
            chromeClient.onHideCustomView();
            return;
        }
        if (webView == null) { finish(); return; }
        webView.evaluateJavascript("(function(){var o=document.getElementById('ov');" +
            "if(o&&o.classList.contains('open')&&typeof closeOv==='function'){closeOv();return true;}" +
            "return false;})()", result -> {
                if (!"true".equals(result)) finish();
            });
    }

    @Override protected void onPause() {
        if (webView != null) {
            webView.evaluateJavascript("var v=document.getElementById('vd');if(v)v.pause();", null);
            webView.onPause();
        }
        super.onPause();
    }
    @Override protected void onResume() {
        super.onResume();
        immersive();
        if (webView != null) {
            webView.onResume();
            webView.evaluateJavascript("if(typeof schedulePreview==='function'){" +
                "var o=document.getElementById('ov');" +
                "if(o&&o.classList.contains('open')){var v=document.getElementById('vd');if(v)v.play().catch(function(){});}" +
                "else schedulePreview();}", null);
        }
    }
    @Override protected void onDestroy() {
        if (webView != null) {
            root.removeView(webView);
            webView.destroy();
            webView = null;
        }
        super.onDestroy();
    }
}
