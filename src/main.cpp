#include <QCommandLineParser>
#include <QGuiApplication>
#include <QObject>
#include <QQmlApplicationEngine>
#include <QString>
#include <QTimer>
#include <Qt>

int main(int argc, char* argv[]) {
    QGuiApplication app(argc, argv);
    QGuiApplication::setApplicationName("HyprPeek");
    QGuiApplication::setApplicationVersion(QStringLiteral(HYPRPEEK_VERSION));

    QCommandLineParser parser;
    parser.addHelpOption();
    parser.addVersionOption();
    parser.addOption({"smoke-test", "Load QML and exit after a short startup check."});
    parser.process(app);

    QQmlApplicationEngine engine;
    QObject::connect(
        &engine, &QQmlApplicationEngine::objectCreationFailed, &app,
        [] { QCoreApplication::exit(1); }, Qt::QueuedConnection);
    engine.loadFromModule("HyprPeek", "Main");
    if (engine.rootObjects().isEmpty()) {
        return 1;
    }

    if (parser.isSet("smoke-test")) {
        QTimer::singleShot(200, &app, &QCoreApplication::quit);
    }

    return QGuiApplication::exec();
}
