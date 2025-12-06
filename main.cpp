#include "include/cef_app.h"
#include "include/cef_browser.h"
#include "include/cef_client.h"

class SimpleHandler : public CefClient, public CefLifeSpanHandler {
public:
    CefRefPtr<CefLifeSpanHandler> GetLifeSpanHandler() override { return this; }
    void OnAfterCreated(CefRefPtr<CefBrowser> browser) override {}
private:
    IMPLEMENT_REFCOUNTING(SimpleHandler);
};

int main(int argc, char** argv) {
    CefMainArgs main_args(argc, argv);
    CefRefPtr<CefApp> app;

    CefSettings settings;
    settings.no_sandbox = true;
    CefInitialize(main_args, settings, app, nullptr);

    CefWindowInfo window_info;
    window_info.SetAsPopup(NULL, "DZCbrowser");

    CefBrowserSettings browser_settings;

    CefBrowserHost::CreateBrowserSync(
        window_info,
        new SimpleHandler(),
        "https://www.google.com",
        browser_settings,
        nullptr,
        nullptr
    );

    CefRunMessageLoop();
    CefShutdown();
    return 0;
}
