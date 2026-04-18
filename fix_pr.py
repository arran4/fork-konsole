import sys

def modify(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # 1. Store enableShellCheck in Private
    # Let's find the Private struct
    search_private = '''struct QuickCommandsWidget::Private {
  QuickCommandsModel *model = nullptr;
  FilterModel *filterModel = nullptr;
  Konsole::SessionController *controller = nullptr;
  bool hasShellCheck = false;
  bool isSetup = false;
  QTimer shellCheckTimer;
};'''
    replace_private = '''struct QuickCommandsWidget::Private {
  QuickCommandsModel *model = nullptr;
  FilterModel *filterModel = nullptr;
  Konsole::SessionController *controller = nullptr;
  bool hasShellCheck = false;
  bool enableShellCheck = true;
  bool isSetup = false;
  QTimer shellCheckTimer;
};'''
    if search_private in content:
        content = content.replace(search_private, replace_private)
    else:
        print("Could not find struct Private to replace!")

    # 2. Re-use single QSettings in QuickCommandsWidget constructor
    search_settings_init = '''  QSettings s;
  s.beginGroup(QStringLiteral("quickcommands"));
  bool enableShellCheck =
      s.value(QStringLiteral("enableShellCheck"), true).toBool();
  priv->hasShellCheck =
      !QStandardPaths::findExecutable(QStringLiteral("shellcheck")).isEmpty();
  if (enableShellCheck && !priv->hasShellCheck) {'''
    replace_settings_init = '''  QSettings settings;
  settings.beginGroup(QStringLiteral("plugins"));
  settings.beginGroup(QStringLiteral("quickcommands"));
  priv->enableShellCheck =
      settings.value(QStringLiteral("enableShellCheck"), true).toBool();
  priv->hasShellCheck =
      !QStandardPaths::findExecutable(QStringLiteral("shellcheck")).isEmpty();
  if (priv->enableShellCheck && !priv->hasShellCheck) {'''
    if search_settings_init in content:
        content = content.replace(search_settings_init, replace_settings_init)
    else:
        print("Could not find initial settings logic to replace!")

    search_settings_shortcut = '''  QSettings settings;
  settings.beginGroup(QStringLiteral("plugins"));
  settings.beginGroup(QStringLiteral("quickcommands"));

  const QKeySequence def(Qt::CTRL | Qt::ALT | Qt::Key_G);'''
    replace_settings_shortcut = '''  const QKeySequence def(Qt::CTRL | Qt::ALT | Qt::Key_G);'''
    if search_settings_shortcut in content:
        content = content.replace(search_settings_shortcut, replace_settings_shortcut)
    else:
        print("Could not find shortcut settings logic to replace!")


    # 3. Add return after warning in invokeCommand
    search_invoke = '''void QuickCommandsWidget::invokeCommand(const QModelIndex &idx) {
  if (!ui->warning->toPlainText().isEmpty()) {
    ui->warningMessage->setMessageType(KMessageWidget::Warning);
    ui->warningMessage->setText(
        i18n("Please fix all the warnings before trying to run this script"));
    ui->warningMessage->animatedShow();
  }'''
    replace_invoke = '''void QuickCommandsWidget::invokeCommand(const QModelIndex &idx) {
  if (!ui->warning->toPlainText().isEmpty()) {
    ui->warningMessage->setMessageType(KMessageWidget::Warning);
    ui->warningMessage->setText(
        i18n("Please fix all the warnings before trying to run this script"));
    ui->warningMessage->animatedShow();
    return;
  }'''
    if search_invoke in content:
        content = content.replace(search_invoke, replace_invoke)
    else:
        print("Could not find invokeCommand to replace!")

    # 4. Remove QSettings re-read in runCommand and use cached priv->enableShellCheck
    search_run_cmd = '''void QuickCommandsWidget::runCommand() {
  if (!priv->hasShellCheck) {
    // check again
    QSettings s;
    s.beginGroup(QStringLiteral("quickcommands"));
    bool enableShellCheck =
        s.value(QStringLiteral("enableShellCheck"), true).toBool();
    priv->hasShellCheck =
        !QStandardPaths::findExecutable(QStringLiteral("shellcheck")).isEmpty();
    if (priv->hasShellCheck) {
      ui->warning->clear();
    }
  }'''
    replace_run_cmd = '''void QuickCommandsWidget::runCommand() {
  if (!priv->hasShellCheck) {
    // check again
    priv->hasShellCheck =
        !QStandardPaths::findExecutable(QStringLiteral("shellcheck")).isEmpty();
    if (priv->enableShellCheck && priv->hasShellCheck) {
      ui->warning->clear();
    }
  }'''
    if search_run_cmd in content:
        content = content.replace(search_run_cmd, replace_run_cmd)
    else:
        print("Could not find runCommand to replace!")

    # 5. Remove QSettings re-read in runShellCheck
    search_run_shellcheck = '''void QuickCommandsWidget::runShellCheck() {
  QSettings settings;
  settings.beginGroup(QStringLiteral("quickcommands"));
  bool enableShellCheck =
      settings.value(QStringLiteral("enableShellCheck"), true).toBool();
  if (!enableShellCheck || !priv->hasShellCheck) {
    return;
  }'''
    replace_run_shellcheck = '''void QuickCommandsWidget::runShellCheck() {
  if (!priv->enableShellCheck || !priv->hasShellCheck) {
    return;
  }'''
    if search_run_shellcheck in content:
        content = content.replace(search_run_shellcheck, replace_run_shellcheck)
    else:
        print("Could not find runShellCheck to replace!")

    with open(filepath, 'w') as f:
        f.write(content)

modify('src/plugins/QuickCommands/quickcommandswidget.cpp')
