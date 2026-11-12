#include <QApplication>
#include <QRegularExpression>

class QRegExp {
    QRegularExpression m_re;
    mutable QRegularExpressionMatch m_match;
public:
    QRegExp() = default;
    explicit QRegExp(const QString &pattern, Qt::CaseSensitivity cs = Qt::CaseSensitive)
        : m_re(pattern, (cs == Qt::CaseInsensitive ? QRegularExpression::CaseInsensitiveOption : QRegularExpression::NoPatternOption) | QRegularExpression::DotMatchesEverythingOption) {}
    int indexIn(const QString &str, int offset = 0) const {
        m_match = m_re.match(str, offset);
        return m_match.hasMatch() ? m_match.capturedStart() : -1;
    }
    QString cap(int nth = 0) const { return m_match.captured(nth); }
    int matchedLength() const { return m_match.capturedLength(); }
    int pos(int nth = 0) const { return m_match.capturedStart(nth); }
    static QString escape(const QString &str) { return QRegularExpression::escape(str); }
    operator QRegularExpression() const { return m_re; }
};
#include <QBrush>
#include <QColor>
#include <QEasingCurve>
#include <QFont>
#include <QGraphicsObject>
#include <QGraphicsScene>
#include <QGraphicsTextItem>
#include <QGraphicsView>
#include <QHBoxLayout>
#include <QPainter>
#include <QParallelAnimationGroup>
#include <QPen>
#include <QPointF>
#include <QPropertyAnimation>
#include <QPushButton>
#include <QRectF>
#include <QRegularExpression>
#include <QSequentialAnimationGroup>
#include <QTextEdit>
#include <QTimer>
#include <QVBoxLayout>
#include <QWidget>

#include <cstdlib>
#include <ctime>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

// ============================================================================
// ДОПОМІЖНІ ФУНКЦІЇ КОНВЕРТАЦІЇ ДЛЯ C++98
// ============================================================================
static QString toQStr(int v) {
    std::ostringstream oss;
    oss << v;
    return QString::fromStdString(oss.str());
}

static QString toQStr(double v, int prec = 2) {
    std::ostringstream oss;
    oss.precision(prec);
    oss << std::fixed << v;
    std::string s = oss.str();
    if (s.find('.') != std::string::npos) {
        while (!s.empty() && s[s.size() - 1] == '0') {
            s.erase(s.size() - 1);
        }
        if (!s.empty() && s[s.size() - 1] == '.') {
            s.erase(s.size() - 1);
        }
    }
    return QString::fromStdString(s);
}

static QString trimQ(const QString& s) {
    return s.trimmed();
}

// ============================================================================
// КРОК 1 ТЗ: КАСТОМНИЙ ГРАФІЧНИЙ КЛАС AnimatedArrayBlock (QGraphicsObject)
// ============================================================================
class AnimatedArrayBlock : public QGraphicsObject {
    Q_OBJECT
    Q_PROPERTY(QColor bgColor READ bgColor WRITE setBgColor)
    Q_PROPERTY(QColor textColor READ textColor WRITE setTextColor)

public:
    AnimatedArrayBlock(const QString& text = "",
                       qreal width = 65.0,
                       qreal height = 40.0,
                       const QString& bgColor = "#ffcc66",
                       const QString& textColor = "#000000",
                       QGraphicsItem* parent = 0)
        : QGraphicsObject(parent),
          m_width(width),
          m_height(height),
          m_text(text),
          m_bgColor(bgColor),
          m_textColor(textColor),
          m_borderColor("#333333"),
          m_font("Arial", 12) {
        setTransformOriginPoint(m_width / 2.0, m_height / 2.0);
    }

    QRectF boundingRect() const {
        qreal penWidth = 1.0;
        return QRectF(-penWidth / 2.0, -penWidth / 2.0,
                      m_width + penWidth, m_height + penWidth);
    }

    void paint(QPainter* painter, const QStyleOptionGraphicsItem* option, QWidget* widget) {
        Q_UNUSED(option);
        Q_UNUSED(widget);

        QRectF rect(0.0, 0.0, m_width, m_height);
        painter->setRenderHint(QPainter::Antialiasing, true);
        painter->setPen(QPen(m_borderColor, 1.0));
        painter->setBrush(QBrush(m_bgColor));
        painter->drawRect(rect);

        painter->setPen(QPen(m_textColor));
        painter->setFont(m_font);
        painter->drawText(rect, Qt::AlignCenter, m_text);
    }

    QColor bgColor() const { return m_bgColor; }
    void setBgColor(const QColor& color) {
        if (m_bgColor != color) {
            m_bgColor = color;
            update();
        }
    }

    void setBgColorStr(const QString& colorStr) {
        setBgColor(QColor(colorStr));
    }

    QColor textColor() const { return m_textColor; }
    void setTextColor(const QColor& color) {
        if (m_textColor != color) {
            m_textColor = color;
            update();
        }
    }

    void setText(const QString& text) {
        if (m_text != text) {
            m_text = text;
            update();
        }
    }

    QString text() const { return m_text; }

private:
    qreal m_width;
    qreal m_height;
    QString m_text;
    QColor m_bgColor;
    QColor m_textColor;
    QColor m_borderColor;
    QFont m_font;
};

// ============================================================================
// КРОК 3 ТЗ: ОБРОБНИК АНІМАЦІЙ CartoonAnimationHandler (QPropertyAnimation)
// ============================================================================
class CartoonAnimationHandler {
public:
    static QPropertyAnimation* animatePushBack(AnimatedArrayBlock* blockItem,
                                               const QPointF& targetPos,
                                               int duration = 320,
                                               QObject* parent = 0) {
        blockItem->setTransformOriginPoint(blockItem->boundingRect().center());
        blockItem->setPos(targetPos);
        blockItem->setOpacity(1.0);
        blockItem->setScale(0.0);

        QPropertyAnimation* scaleAnim = new QPropertyAnimation(blockItem, "scale", parent);
        scaleAnim->setDuration(duration);
        scaleAnim->setStartValue(0.0);
        scaleAnim->setEndValue(1.0);
        scaleAnim->setEasingCurve(QEasingCurve::OutBounce);
        return scaleAnim;
    }

    static QParallelAnimationGroup* animatePop(AnimatedArrayBlock* blockItem,
                                               QGraphicsScene* scene,
                                               int duration = 300,
                                               QObject* parent = 0) {
        Q_UNUSED(scene);
        blockItem->setTransformOriginPoint(blockItem->boundingRect().center());
        QParallelAnimationGroup* group = new QParallelAnimationGroup(parent);

        QPropertyAnimation* scaleAnim = new QPropertyAnimation(blockItem, "scale", group);
        scaleAnim->setDuration(duration);
        scaleAnim->setStartValue(blockItem->scale());
        scaleAnim->setEndValue(0.0);
        scaleAnim->setEasingCurve(QEasingCurve::InBack);

        QPropertyAnimation* opacityAnim = new QPropertyAnimation(blockItem, "opacity", group);
        opacityAnim->setDuration(duration);
        opacityAnim->setStartValue(blockItem->opacity());
        opacityAnim->setEndValue(0.0);

        group->addAnimation(scaleAnim);
        group->addAnimation(opacityAnim);
        QObject::connect(group, SIGNAL(finished()), blockItem, SLOT(deleteLater()));
        return group;
    }

    static QSequentialAnimationGroup* animateChange(AnimatedArrayBlock* blockItem,
                                                    const QString& newValue,
                                                    const QString& newBgColor = "#ff9999",
                                                    int duration = 320,
                                                    QObject* parent = 0) {
        blockItem->setTransformOriginPoint(blockItem->boundingRect().center());
        blockItem->setBgColorStr(newBgColor);
        blockItem->setText(newValue);

        QSequentialAnimationGroup* seqGroup = new QSequentialAnimationGroup(parent);
        int halfDur = duration / 2 > 10 ? duration / 2 : 10;

        QPropertyAnimation* growAnim = new QPropertyAnimation(blockItem, "scale", seqGroup);
        growAnim->setDuration(halfDur);
        growAnim->setStartValue(1.0);
        growAnim->setEndValue(1.2);
        growAnim->setEasingCurve(QEasingCurve::OutQuad);

        QPropertyAnimation* shrinkAnim = new QPropertyAnimation(blockItem, "scale", seqGroup);
        shrinkAnim->setDuration(halfDur);
        shrinkAnim->setStartValue(1.2);
        shrinkAnim->setEndValue(1.0);
        shrinkAnim->setEasingCurve(QEasingCurve::OutBack);

        seqGroup->addAnimation(growAnim);
        seqGroup->addAnimation(shrinkAnim);
        return seqGroup;
    }
};

// ============================================================================
// СТРУКТУРА СТАНУ КРОКУ ВИКОНАННЯ
// ============================================================================
struct ExecutionStep {
    std::map<QString, std::vector<double> > arrays;
    std::vector<QString> arrayOrder;
    QString description;
    bool showSumAvg;
    bool hasConditionCount;
    int conditionCount;
    std::vector<int> maxIndices;
    bool hasMaxVal;
    double currentMaxVal;
    bool hasMinVal;
    double currentMinVal;
    std::vector<int> minIndices;
    bool hasTempVal;
    double tempVal;
    std::vector<int> pairIndices;
    bool showCapacitySize;
    int capacityMetric;
    int sizeMetric;
    int searchIndex;
    int foundIndex;
    bool hasBinaryRange;
    int binaryLow;
    int binaryHigh;
    int binaryMid;
    int pivotIndex;
    std::map<QString, double> extraVars;
    int precision;

    ExecutionStep()
        : showSumAvg(false),
          hasConditionCount(false),
          conditionCount(0),
          hasMaxVal(false),
          currentMaxVal(0.0),
          hasMinVal(false),
          currentMinVal(0.0),
          hasTempVal(false),
          tempVal(0.0),
          showCapacitySize(false),
          capacityMetric(-1),
          sizeMetric(-1),
          searchIndex(-1),
          foundIndex(-1),
          hasBinaryRange(false),
          binaryLow(0),
          binaryHigh(0),
          binaryMid(-1),
          pivotIndex(-1),
          precision(2) {}
};

// ============================================================================
// КРОК 2, 3, 4 ТЗ: ВІДЖЕТ АНІМАЦІЇ AdaptiveAnimationWidget
// ============================================================================
class AdaptiveAnimationWidget : public QWidget {
    Q_OBJECT

public:
    explicit AdaptiveAnimationWidget(QWidget* parent = 0)
        : QWidget(parent),
          m_scene(new QGraphicsScene(this)),
          m_view(new QGraphicsView(m_scene, this)),
          m_blockWidth(65.0),
          m_blockHeight(40.0),
          m_spacing(8.0),
          m_baseX(75.0),
          m_baseY(150.0),
          m_activeAnimationGroup(0),
          m_animDuration(300),
          m_metricsItem(0),
          m_tempBlock(0),
          m_tempLabel(0) {
        m_view->setRenderHint(QPainter::Antialiasing, true);

        QVBoxLayout* layout = new QVBoxLayout(this);
        layout->setContentsMargins(0, 0, 0, 0);
        layout->addWidget(m_view);
    }

    void setAnimationSpeed(int stepIntervalMs) {
        int dur = static_cast<int>(stepIntervalMs * 0.75);
        if (dur < 80) dur = 80;
        if (dur > 350) dur = 350; // Не більше 350 мс згідно п. 4 ТЗ
        m_animDuration = dur;
    }

    void reset() {
        if (m_activeAnimationGroup &&
            m_activeAnimationGroup->state() == QAbstractAnimation::Running) {
            m_activeAnimationGroup->stop();
        }
        m_scene->clear();
        m_arrayRows.clear();
        m_staticItems.clear();
        m_metricsItem = 0;
        m_tempBlock = 0;
        m_tempLabel = 0;
    }

    void clearStaticLayer() {
        for (std::size_t i = 0; i < m_staticItems.size(); ++i) {
            if (m_staticItems[i]->scene() == m_scene) {
                m_scene->removeItem(m_staticItems[i]);
            }
            delete m_staticItems[i];
        }
        m_staticItems.clear();
    }

    QPointF getTargetPos(int index, int rowIdx = 0) const {
        qreal rowY = m_baseY + rowIdx * (m_blockHeight + 45.0);
        return QPointF(m_baseX + index * (m_blockWidth + m_spacing), rowY);
    }

    void finalizeRunningAnimations() {
        if (m_activeAnimationGroup &&
            m_activeAnimationGroup->state() == QAbstractAnimation::Running) {
            m_activeAnimationGroup->stop();
        }
        for (std::map<QString, ArrayRowData>::iterator it = m_arrayRows.begin();
             it != m_arrayRows.end(); ++it) {
            std::vector<BlockData>& blocks = it->second.blocks;
            for (std::size_t i = 0; i < blocks.size(); ++i) {
                blocks[i].item->setScale(1.0);
                blocks[i].item->setOpacity(1.0);
            }
        }
    }

    void updateVariables(const ExecutionStep& step) {
        clearStaticLayer();
        finalizeRunningAnimations();

        QParallelAnimationGroup* animGroup = new QParallelAnimationGroup(this);

        // 1. Текстовий коментар до кроку
        if (!step.description.isEmpty()) {
            QGraphicsTextItem* descItem = m_scene->addText(step.description);
            descItem->setFont(QFont("Consolas", 13, QFont::Bold));
            descItem->setDefaultTextColor(QColor("#2c3e50"));
            descItem->setPos(15.0, m_baseY - 75.0);
            m_staticItems.push_back(descItem);
        }

        // 2. Контекстні метрики
        QStringList metricsParts;
        if (step.showCapacitySize) {
            QStringList csList;
            if (step.capacityMetric >= 0) {
                csList << ("Місткість (Capacity): " + toQStr(step.capacityMetric));
            }
            int totalElements = 0;
            for (std::map<QString, std::vector<double> >::const_iterator it = step.arrays.begin();
                 it != step.arrays.end(); ++it) {
                totalElements += static_cast<int>(it->second.size());
            }
            int szVal = (step.sizeMetric >= 0) ? step.sizeMetric : totalElements;
            csList << ("Кількість (Size): " + toQStr(szVal));
            metricsParts << csList.join(" | ");
        }

        if (step.showSumAvg) {
            const std::vector<double>* firstVals = 0;
            for (std::size_t i = 0; i < step.arrayOrder.size(); ++i) {
                std::map<QString, std::vector<double> >::const_iterator it =
                    step.arrays.find(step.arrayOrder[i]);
                if (it != step.arrays.end() && !it->second.empty()) {
                    firstVals = &it->second;
                    break;
                }
            }
            if (firstVals && !firstVals->empty()) {
                double currSum = 0.0;
                for (std::size_t i = 0; i < firstVals->size(); ++i) {
                    currSum += (*firstVals)[i];
                }
                double currAvg = currSum / static_cast<double>(firstVals->size());
                metricsParts << ("Сума: " + toQStr(currSum, step.precision) +
                                 " | Сер: " + toQStr(currAvg, 2));
            } else {
                metricsParts << "Сума: 0 | Сер: 0.00";
            }
        }

        // Умовні суми
        if (!step.extraVars.empty()) {
            QStringList condSums;
            for (std::map<QString, double>::const_iterator it = step.extraVars.begin();
                 it != step.extraVars.end(); ++it) {
                QString kLower = it->first.toLower();
                if (kLower.contains("sum") && kLower != "sum" &&
                    kLower != "curr_sum" && kLower != "sum_val") {
                    QString label = it->first;
                    if (kLower.contains("positive") || kLower.contains("pos")) {
                        label = "Сума додатних (" + it->first + ")";
                    } else if (kLower.contains("negative") || kLower.contains("neg")) {
                        label = "Сума від'ємних (" + it->first + ")";
                    } else if (kLower.contains("even")) {
                        label = "Сума парних (" + it->first + ")";
                    } else if (kLower.contains("odd")) {
                        label = "Сума непарних (" + it->first + ")";
                    }
                    condSums << (label + ": " + toQStr(it->second, step.precision));
                }
            }
            if (!condSums.isEmpty()) {
                metricsParts << condSums.join(" | ");
            }
        }

        // Лічильники
        QStringList activeCnts;
        for (std::map<QString, double>::const_iterator it = step.extraVars.begin();
             it != step.extraVars.end(); ++it) {
            QString kLower = it->first.toLower();
            if ((kLower.contains("count") || kLower.contains("counter") ||
                 kLower.contains("matched") || kLower.contains("num_")) &&
                kLower != "count_metric" && kLower != "capacity" && kLower != "size") {
                activeCnts << (it->first + ": " + toQStr(it->second, 0));
            }
        }
        if (!activeCnts.isEmpty()) {
            metricsParts << activeCnts.join(" | ");
        } else if (step.hasConditionCount && !step.showCapacitySize) {
            metricsParts << ("Кількість за умовою: " + toQStr(step.conditionCount));
        }

        if (step.hasMinVal) {
            QString idxsStr;
            if (!step.minIndices.empty()) {
                QStringList idxList;
                for (std::size_t i = 0; i < step.minIndices.size(); ++i) {
                    idxList << toQStr(step.minIndices[i]);
                }
                idxsStr = " [індекси: " + idxList.join(", ") + "]";
            }
            metricsParts << ("Мінімум (Min): " + toQStr(step.currentMinVal, step.precision) + idxsStr);
        }

        if (step.hasMaxVal) {
            QString idxsStr;
            if (!step.maxIndices.empty()) {
                QStringList idxList;
                for (std::size_t i = 0; i < step.maxIndices.size(); ++i) {
                    idxList << toQStr(step.maxIndices[i]);
                }
                idxsStr = " [індекси: " + idxList.join(", ") + "]";
            }
            metricsParts << ("Максимум (Max): " + toQStr(step.currentMaxVal, step.precision) + idxsStr);
        }

        if (step.foundIndex >= 0) {
            metricsParts << ("Знайдено індекс: " + toQStr(step.foundIndex));
        } else if (step.binaryMid >= 0 && step.hasBinaryRange) {
            metricsParts << ("Діапазон: [" + toQStr(step.binaryLow) + "..." +
                             toQStr(step.binaryHigh) + "] | mid: " + toQStr(step.binaryMid));
        }

        if (!metricsParts.isEmpty()) {
            QString metricsStr = metricsParts.join("   |   ");
            if (!m_metricsItem) {
                m_metricsItem = m_scene->addText(metricsStr);
                m_metricsItem->setFont(QFont("Consolas", 11, QFont::Bold));
                m_metricsItem->setDefaultTextColor(QColor("#16a085"));
                m_metricsItem->setPos(15.0, m_baseY - 35.0);
            } else {
                m_metricsItem->setPlainText(metricsStr);
                m_metricsItem->setVisible(true);
            }
        } else if (m_metricsItem) {
            m_metricsItem->setVisible(false);
        }

        // 3. Блок буферної змінної temp
        if (step.hasTempVal) {
            QPointF tempPos(m_baseX + 40.0, m_baseY - 125.0);
            QString tempStr = toQStr(step.tempVal, step.precision);
            if (!m_tempBlock) {
                m_tempLabel = m_scene->addText("temp:");
                m_tempLabel->setFont(QFont("Consolas", 11, QFont::Bold));
                m_tempLabel->setDefaultTextColor(QColor("#8e44ad"));
                m_tempLabel->setPos(m_baseX - 15.0, m_baseY - 117.0);

                m_tempBlock = new AnimatedArrayBlock(tempStr, m_blockWidth, m_blockHeight,
                                                     "#9b59b6", "#ffffff");
                m_scene->addItem(m_tempBlock);
                QPropertyAnimation* anim = CartoonAnimationHandler::animatePushBack(
                    m_tempBlock, tempPos, m_animDuration, this);
                anim->start(QAbstractAnimation::DeleteWhenStopped);
            } else {
                m_tempBlock->setText(tempStr);
                m_tempBlock->setBgColorStr("#9b59b6");
                QSequentialAnimationGroup* chAnim = CartoonAnimationHandler::animateChange(
                    m_tempBlock, tempStr, "#8e44ad", m_animDuration, this);
                chAnim->start(QAbstractAnimation::DeleteWhenStopped);
            }
        } else {
            if (m_tempBlock) {
                QParallelAnimationGroup* popAnim = CartoonAnimationHandler::animatePop(
                    m_tempBlock, m_scene, m_animDuration, this);
                popAnim->start(QAbstractAnimation::DeleteWhenStopped);
                m_tempBlock = 0;
            }
            if (m_tempLabel) {
                m_scene->removeItem(m_tempLabel);
                delete m_tempLabel;
                m_tempLabel = 0;
            }
        }

        // Визначення активного масиву
        QString activeTargetArr;
        for (std::size_t i = 0; i < step.arrayOrder.size(); ++i) {
            const QString& aname = step.arrayOrder[i];
            if (step.description.contains(aname + "[") ||
                step.description.contains(aname + ".") ||
                step.description.contains("(" + aname + ")")) {
                activeTargetArr = aname;
                break;
            }
        }

        // Видалення рядків масивів, яких більше немає
        std::vector<QString> toErase;
        for (std::map<QString, ArrayRowData>::iterator it = m_arrayRows.begin();
             it != m_arrayRows.end(); ++it) {
            if (step.arrays.find(it->first) == step.arrays.end()) {
                if (it->second.label->scene() == m_scene) {
                    m_scene->removeItem(it->second.label);
                }
                delete it->second.label;
                for (std::size_t b = 0; b < it->second.blocks.size(); ++b) {
                    if (it->second.blocks[b].item->scene() == m_scene) {
                        m_scene->removeItem(it->second.blocks[b].item);
                    }
                    delete it->second.blocks[b].item;
                }
                toErase.push_back(it->first);
            }
        }
        for (std::size_t i = 0; i < toErase.size(); ++i) {
            m_arrayRows.erase(toErase[i]);
        }

        std::set<int> maxIdxSet(step.maxIndices.begin(), step.maxIndices.end());
        std::set<int> pairIdxSet(step.pairIndices.begin(), step.pairIndices.end());

        // Відображення кожного масиву
        for (std::size_t r = 0; r < step.arrayOrder.size(); ++r) {
            const QString& arrName = step.arrayOrder[r];
            std::map<QString, std::vector<double> >::const_iterator arrIt = step.arrays.find(arrName);
            if (arrIt == step.arrays.end()) continue;

            const std::vector<double>& vals = arrIt->second;
            int rowIdx = static_cast<int>(r);
            qreal rowY = m_baseY + rowIdx * (m_blockHeight + 45.0);

            if (m_arrayRows.find(arrName) == m_arrayRows.end()) {
                QGraphicsTextItem* lbl = m_scene->addText(arrName + ":");
                lbl->setFont(QFont("Consolas", 12, QFont::Bold));
                lbl->setDefaultTextColor(QColor("#2c3e50"));
                lbl->setPos(15.0, rowY + 8.0);
                ArrayRowData rowData;
                rowData.label = lbl;
                m_arrayRows[arrName] = rowData;
            } else {
                QGraphicsTextItem* lbl = m_arrayRows[arrName].label;
                lbl->setPos(15.0, rowY + 8.0);
                lbl->setPlainText(arrName + ":");
            }

            std::vector<BlockData>& blocksList = m_arrayRows[arrName].blocks;
            int oldCount = static_cast<int>(blocksList.size());
            int newCount = static_cast<int>(vals.size());
            int minLen = (oldCount < newCount) ? oldCount : newCount;

            bool isActiveRow = (activeTargetArr.isEmpty() || arrName == activeTargetArr);

            for (int i = 0; i < minLen; ++i) {
                BlockData& bData = blocksList[static_cast<std::size_t>(i)];
                AnimatedArrayBlock* blockItem = bData.item;
                double oldVal = bData.value;
                double newVal = vals[static_cast<std::size_t>(i)];

                QString targetColor = "#33ccff";
                if (isActiveRow && step.pivotIndex >= 0 && i == step.pivotIndex) {
                    targetColor = "#e74c3c";
                } else if (isActiveRow && step.foundIndex >= 0 && i == step.foundIndex) {
                    targetColor = "#2ecc71";
                } else if (isActiveRow && step.binaryMid >= 0 && i == step.binaryMid) {
                    targetColor = "#e67e22";
                } else if (isActiveRow && step.hasBinaryRange) {
                    if (step.binaryLow <= i && i <= step.binaryHigh) {
                        targetColor = "#3498db";
                    } else {
                        targetColor = "#bdc3c7";
                    }
                } else if (isActiveRow && step.searchIndex >= 0 && i == step.searchIndex) {
                    targetColor = "#f1c40f";
                } else if (isActiveRow && pairIdxSet.count(i) > 0) {
                    targetColor = "#e056fd";
                } else if (isActiveRow && maxIdxSet.count(i) > 0) {
                    targetColor = "#f39c12";
                }

                if (oldVal != newVal) {
                    bData.value = newVal;
                    QSequentialAnimationGroup* pulseAnim = CartoonAnimationHandler::animateChange(
                        blockItem, toQStr(newVal, step.precision), targetColor, m_animDuration, animGroup);
                    animGroup->addAnimation(pulseAnim);
                } else {
                    blockItem->setBgColorStr(targetColor);
                }
            }

            // Сценарій А: Додавання елементів (push_back)
            if (newCount > oldCount) {
                for (int i = oldCount; i < newCount; ++i) {
                    double val = vals[static_cast<std::size_t>(i)];
                    QPointF targetPos = getTargetPos(i, rowIdx);
                    QString color = "#99ff99";
                    if (isActiveRow && step.foundIndex == i) color = "#2ecc71";
                    else if (isActiveRow && pairIdxSet.count(i) > 0) color = "#e056fd";
                    else if (isActiveRow && maxIdxSet.count(i) > 0) color = "#f39c12";

                    AnimatedArrayBlock* newBlock = new AnimatedArrayBlock(
                        toQStr(val, step.precision), m_blockWidth, m_blockHeight, color);
                    m_scene->addItem(newBlock);

                    QPropertyAnimation* bounceAnim = CartoonAnimationHandler::animatePushBack(
                        newBlock, targetPos, m_animDuration, animGroup);
                    animGroup->addAnimation(bounceAnim);

                    BlockData bd;
                    bd.item = newBlock;
                    bd.value = val;
                    blocksList.push_back(bd);
                }
            }
            // Сценарій Б: Видалення елементів (pop)
            else if (newCount < oldCount) {
                for (int i = newCount; i < oldCount; ++i) {
                    AnimatedArrayBlock* blockItem = blocksList[static_cast<std::size_t>(i)].item;
                    blockItem->setBgColorStr("#e74c3c");
                    animGroup->addAnimation(CartoonAnimationHandler::animatePop(
                        blockItem, m_scene, m_animDuration, animGroup));
                }
                blocksList.resize(static_cast<std::size_t>(newCount));
            }

            // Синхронізація тексту та позицій
            for (int i = 0; i < static_cast<int>(blocksList.size()); ++i) {
                if (i < newCount) {
                    blocksList[static_cast<std::size_t>(i)].value = vals[static_cast<std::size_t>(i)];
                    blocksList[static_cast<std::size_t>(i)].item->setText(
                        toQStr(vals[static_cast<std::size_t>(i)], step.precision));
                }
                QPointF targetPos = getTargetPos(i, rowIdx);
                if (blocksList[static_cast<std::size_t>(i)].item->pos() != targetPos) {
                    blocksList[static_cast<std::size_t>(i)].item->setPos(targetPos);
                }
            }
        }

        m_activeAnimationGroup = animGroup;
        animGroup->start(QAbstractAnimation::DeleteWhenStopped);
    }

private:
    struct BlockData {
        AnimatedArrayBlock* item;
        double value;
    };

    struct ArrayRowData {
        QGraphicsTextItem* label;
        std::vector<BlockData> blocks;
    };

    QGraphicsScene* m_scene;
    QGraphicsView* m_view;
    std::map<QString, ArrayRowData> m_arrayRows;
    std::vector<QGraphicsTextItem*> m_staticItems;
    qreal m_blockWidth;
    qreal m_blockHeight;
    qreal m_spacing;
    qreal m_baseX;
    qreal m_baseY;
    QParallelAnimationGroup* m_activeAnimationGroup;
    int m_animDuration;
    QGraphicsTextItem* m_metricsItem;
    AnimatedArrayBlock* m_tempBlock;
    QGraphicsTextItem* m_tempLabel;
};

// ============================================================================
// УНІВЕРСАЛЬНИЙ ПАРСЕР ТА РУШІЙ ВИКОНАННЯ КОДУ C++98
// ============================================================================
class CppUniversalEngine {
public:
    CppUniversalEngine() {
        std::srand(static_cast<unsigned int>(std::time(0)));
        resetState();
    }

    std::vector<ExecutionStep> run(const QString& codeText) {
        resetState();
        std::vector<ExecutionStep> steps;

        QString code = cleanCode(codeText);
        detectFeatures(code);

        // Вилучення тіла int main(...) { ... }
        QRegExp mainRx("int\\s+main\\s*\\([^)]*\\)\\s*\\{(.*)\\}");
        QString body = code;
        if (mainRx.indexIn(code) != -1) {
            body = mainRx.cap(1);
        }

        executeBlock(body, steps);
        return steps;
    }

private:
    std::vector<std::map<QString, double> > m_scopes;
    std::map<QString, std::vector<double> > m_arrays;
    std::vector<QString> m_arrayOrder;
    std::map<QString, int> m_vectorCapacities;
    QString m_mainArrayName;

    bool m_hasTempInCode;
    bool m_hasSumAvg;
    bool m_hasCount;
    bool m_hasMaxSearch;
    bool m_hasCapacitySize;
    bool m_hasLinearSearch;
    bool m_hasBinarySearch;

    bool m_hasConditionCount;
    int m_conditionCount;
    std::vector<int> m_maxIndices;
    bool m_hasMaxVal;
    double m_currentMaxVal;
    bool m_hasMinVal;
    double m_currentMinVal;
    std::vector<int> m_minIndices;
    bool m_hasTempVal;
    double m_tempVal;
    std::vector<int> m_activePair;
    int m_currentCapacity;
    int m_currentSize;
    int m_searchIndex;
    int m_foundIndex;
    bool m_hasBinaryRange;
    int m_binaryLow;
    int m_binaryHigh;
    int m_binaryMid;
    int m_pivotIndex;
    int m_precision;

    void resetState() {
        m_scopes.clear();
        m_scopes.push_back(std::map<QString, double>());
        m_arrays.clear();
        m_arrayOrder.clear();
        m_vectorCapacities.clear();
        m_mainArrayName = "arr";

        m_hasTempInCode = false;
        m_hasSumAvg = false;
        m_hasCount = false;
        m_hasMaxSearch = false;
        m_hasCapacitySize = false;
        m_hasLinearSearch = false;
        m_hasBinarySearch = false;

        m_hasConditionCount = false;
        m_conditionCount = 0;
        m_maxIndices.clear();
        m_hasMaxVal = false;
        m_currentMaxVal = 0.0;
        m_hasMinVal = false;
        m_currentMinVal = 0.0;
        m_minIndices.clear();
        m_hasTempVal = false;
        m_tempVal = 0.0;
        m_activePair.clear();
        m_currentCapacity = -1;
        m_currentSize = -1;
        m_searchIndex = -1;
        m_foundIndex = -1;
        m_hasBinaryRange = false;
        m_binaryLow = 0;
        m_binaryHigh = 0;
        m_binaryMid = -1;
        m_pivotIndex = -1;
        m_precision = 2;
    }

    void pushScope() {
        m_scopes.push_back(std::map<QString, double>());
    }

    void popScope() {
        if (m_scopes.size() > 1) {
            m_scopes.pop_back();
        }
    }

    double getVar(const QString& name, double defVal = 0.0) const {
        for (int i = static_cast<int>(m_scopes.size()) - 1; i >= 0; --i) {
            std::map<QString, double>::const_iterator it =
                m_scopes[static_cast<std::size_t>(i)].find(name);
            if (it != m_scopes[static_cast<std::size_t>(i)].end()) {
                return it->second;
            }
        }
        return defVal;
    }

    bool hasVar(const QString& name) const {
        for (int i = static_cast<int>(m_scopes.size()) - 1; i >= 0; --i) {
            if (m_scopes[static_cast<std::size_t>(i)].find(name) !=
                m_scopes[static_cast<std::size_t>(i)].end()) {
                return true;
            }
        }
        return false;
    }

    void setVar(const QString& name, double val, bool isDecl = false) {
        if (isDecl || m_scopes.empty()) {
            m_scopes.back()[name] = val;
            return;
        }
        for (int i = static_cast<int>(m_scopes.size()) - 1; i >= 0; --i) {
            std::map<QString, double>::iterator it =
                m_scopes[static_cast<std::size_t>(i)].find(name);
            if (it != m_scopes[static_cast<std::size_t>(i)].end()) {
                it->second = val;
                return;
            }
        }
        m_scopes.back()[name] = val;
    }

    void registerArray(const QString& name, const std::vector<double>& vals) {
        if (m_arrays.find(name) == m_arrays.end()) {
            m_arrayOrder.push_back(name);
        }
        m_arrays[name] = vals;
        m_mainArrayName = name;
    }

    ExecutionStep makeStep(const QString& desc) const {
        ExecutionStep st;
        st.arrays = m_arrays;
        st.arrayOrder = m_arrayOrder;
        st.description = desc;
        st.showSumAvg = m_hasSumAvg;
        st.hasConditionCount = m_hasConditionCount;
        st.conditionCount = m_conditionCount;
        st.maxIndices = m_maxIndices;
        st.hasMaxVal = m_hasMaxVal;
        st.currentMaxVal = m_currentMaxVal;
        st.hasMinVal = m_hasMinVal;
        st.currentMinVal = m_currentMinVal;
        st.minIndices = m_minIndices;
        st.hasTempVal = m_hasTempVal && m_hasTempInCode;
        st.tempVal = m_tempVal;
        st.pairIndices = m_activePair;
        st.showCapacitySize = m_hasCapacitySize;
        st.capacityMetric = m_currentCapacity;
        st.sizeMetric = m_currentSize;
        st.searchIndex = m_searchIndex;
        st.foundIndex = m_foundIndex;
        st.hasBinaryRange = m_hasBinaryRange;
        st.binaryLow = m_binaryLow;
        st.binaryHigh = m_binaryHigh;
        st.binaryMid = m_binaryMid;
        st.pivotIndex = m_pivotIndex;
        st.precision = m_precision;

        for (std::size_t s = 0; s < m_scopes.size(); ++s) {
            for (std::map<QString, double>::const_iterator it = m_scopes[s].begin();
                 it != m_scopes[s].end(); ++it) {
                QString kLower = it->first.toLower();
                if ((kLower.contains("count") || kLower.contains("counter") ||
                     kLower.contains("matched") || kLower.contains("num_") ||
                     kLower.contains("sumpositive") || kLower.contains("sumnegative") ||
                     kLower.contains("sumeven") || kLower.contains("sumodd") ||
                     kLower.contains("sumpos") || kLower.contains("sumneg")) &&
                    kLower != "i" && kLower != "j" && kLower != "n" &&
                    kLower != "capacity" && kLower != "size") {
                    st.extraVars[it->first] = it->second;
                }
            }
        }
        return st;
    }

    QString cleanCode(const QString& source) {
        QRegExp precRx("(?:std\\s*::\\s*)?setprecision\\s*\\(\\s*(\\d+)\\s*\\)");
        if (precRx.indexIn(source) != -1) {
            m_precision = precRx.cap(1).toInt();
        }

        // Видалення багаторядкових коментарів
        QString res = source;
        res.replace(QRegularExpression("/\\*.*\\*/"), "");

        // Видалення однорядкових коментарів та директив препроцесора
        QStringList lines = res.split('\n');
        QStringList cleaned;
        for (int i = 0; i < lines.size(); ++i) {
            QString line = lines[i];
            int commentIdx = line.indexOf("//");
            if (commentIdx != -1) {
                line = line.left(commentIdx);
            }
            line = line.trimmed();
            if (line.isEmpty() || line.startsWith("#")) continue;
            cleaned << line;
        }
        QString joined = cleaned.join(" ");
        joined.replace(QRegularExpression("\\busing\\s+namespace\\s+\\w+\\s*;"), "");
        joined.replace(QRegularExpression("\\b(?:std\\s*::\\s*)?cin\\s*>>\\s*[^;]+;"), "");
        return joined;
    }

    void detectFeatures(const QString& code) {
        QString low = code.toLower();
        m_hasTempInCode = low.contains(QRegularExpression("\\btemp\\b"));
        m_hasSumAvg = low.contains(QRegularExpression("\\b(sum|avg|average|mean|accumulate)\\b"));
        m_hasCount = low.contains(QRegularExpression("\\b(count|counter|matched|count_if)\\b"));
        m_hasMaxSearch = low.contains(QRegularExpression("\\b(max|maxval|max_val|max_element|maximum)\\b"));
        m_hasCapacitySize = low.contains(QRegularExpression("\\b(capacity|cap|actual_size|vector|push_back|pop_back|reserve|resize)\\b"));
        m_hasBinarySearch = low.contains(QRegularExpression("\\b(binary_search|binarysearch|mid|low|high)\\b"));
        m_hasLinearSearch = (low.contains(QRegularExpression("\\b(find|search|target|key)\\b")) ||
                             low.contains("== target") || low.contains("target ==")) && !m_hasBinarySearch;
    }

    // Парсер арифметичних та індексних виразів для C++98
    double evalExpression(const QString& rawExpr) {
        QString expr = rawExpr.trimmed();
        if (expr.isEmpty()) return 0.0;

        // Обробка викликів arr.size(), arr.front(), arr.back(), arr.at(i)
        for (std::map<QString, std::vector<double> >::const_iterator it = m_arrays.begin();
             it != m_arrays.end(); ++it) {
            const QString& name = it->first;
            const std::vector<double>& arr = it->second;

            expr.replace(QRegularExpression("\\b" + QRegularExpression::escape(name) + "\\.size\\s*\\(\\s*\\)"),
                         toQStr(static_cast<int>(arr.size())));
            expr.replace(QRegularExpression("\\b" + QRegularExpression::escape(name) + "\\.capacity\\s*\\(\\s*\\)"),
                         toQStr(m_vectorCapacities.count(name) ? m_vectorCapacities[name]
                                                               : static_cast<int>(arr.size())));
            if (!arr.empty()) {
                expr.replace(QRegularExpression("\\b" + QRegularExpression::escape(name) + "\\.front\\s*\\(\\s*\\)"),
                             toQStr(arr.front(), 4));
                expr.replace(QRegularExpression("\\b" + QRegularExpression::escape(name) + "\\.back\\s*\\(\\s*\\)"),
                             toQStr(arr.back(), 4));
            }
        }

        // Підстановка звернень до елементів масиву: arr[idx] або arr.at(idx)
        QRegExp arrAccessRx("\\b([a-zA-Z_]\\w*)\\s*(?:\\[([^\\]]+)\\]|\\.at\\s*\\(([^)]+)\\))");
        int pos = 0;
        while ((pos = arrAccessRx.indexIn(expr, pos)) != -1) {
            QString aname = arrAccessRx.cap(1);
            QString idxStr = !arrAccessRx.cap(2).isEmpty() ? arrAccessRx.cap(2) : arrAccessRx.cap(3);
            if (m_arrays.count(aname)) {
                int idx = static_cast<int>(evalExpression(idxStr));
                const std::vector<double>& arr = m_arrays[aname];
                if (idx >= 0 && idx < static_cast<int>(arr.size())) {
                    QString valStr = toQStr(arr[static_cast<std::size_t>(idx)], 4);
                    expr.replace(pos, arrAccessRx.matchedLength(), valStr);
                    pos += valStr.length();
                    continue;
                }
            }
            pos += arrAccessRx.matchedLength();
        }

        // rand()
        QRegExp randRx("\\brand\\s*\\(\\s*\\)");
        while (randRx.indexIn(expr) != -1) {
            expr.replace(randRx.pos(0), randRx.matchedLength(), toQStr(std::rand() % 100));
        }

        // Видалення приведень типів (double), static_cast<double>(x)
        expr.replace(QRegularExpression("static_cast\\s*<[^>]+>\\s*\\(([^)]+)\\)"), "(\\1)");
        expr.replace(QRegularExpression("\\(\\s*(?:double|float|int|long)\\s*\\)"), "");

        // Підстановка змінних
        QRegExp idRx("\\b([a-zA-Z_]\\w*)\\b");
        pos = 0;
        while ((pos = idRx.indexIn(expr, pos)) != -1) {
            QString vname = idRx.cap(1);
            if (hasVar(vname)) {
                QString numStr = toQStr(getVar(vname), 4);
                expr.replace(pos, idRx.matchedLength(), numStr);
                pos += numStr.length();
            } else {
                pos += idRx.matchedLength();
            }
        }

        return parseAddSub(expr);
    }

    double parseAddSub(const QString& s) {
        QString expr = s.trimmed();
        int depth = 0;
        for (int i = expr.length() - 1; i >= 0; --i) {
            QChar ch = expr[i];
            if (ch == ')') ++depth;
            else if (ch == '(') --depth;
            else if (depth == 0 && i > 0 && (ch == '+' || ch == '-')) {
                QChar prev = expr[i - 1];
                if (prev != '*' && prev != '/' && prev != '%' && prev != '+' && prev != '-' && prev != '(') {
                    double left = parseAddSub(expr.left(i));
                    double right = parseMulDiv(expr.mid(i + 1));
                    return (ch == '+') ? (left + right) : (left - right);
                }
            }
        }
        return parseMulDiv(expr);
    }

    double parseMulDiv(const QString& s) {
        QString expr = s.trimmed();
        int depth = 0;
        for (int i = expr.length() - 1; i >= 0; --i) {
            QChar ch = expr[i];
            if (ch == ')') ++depth;
            else if (ch == '(') --depth;
            else if (depth == 0 && (ch == '*' || ch == '/' || ch == '%')) {
                double left = parseMulDiv(expr.left(i));
                double right = parseAtom(expr.mid(i + 1));
                if (ch == '*') return left * right;
                if (ch == '/') return (right != 0.0) ? (left / right) : 0.0;
                if (ch == '%') return (static_cast<int>(right) != 0)
                                          ? static_cast<double>(static_cast<int>(left) % static_cast<int>(right))
                                          : 0.0;
            }
        }
        return parseAtom(expr);
    }

    double parseAtom(const QString& s) {
        QString expr = s.trimmed();
        if (expr.isEmpty()) return 0.0;
        if (expr.startsWith('(') && expr.endsWith(')')) {
            int depth = 0;
            bool outer = true;
            for (int i = 0; i < expr.length() - 1; ++i) {
                if (expr[i] == '(') ++depth;
                else if (expr[i] == ')') --depth;
                if (depth == 0) {
                    outer = false;
                    break;
                }
            }
            if (outer) {
                return parseAddSub(expr.mid(1, expr.length() - 2));
            }
        }
        if (expr.startsWith('-')) return -parseAtom(expr.mid(1));
        if (expr.startsWith('+')) return parseAtom(expr.mid(1));
        bool ok = false;
        double val = expr.toDouble(&ok);
        return ok ? val : 0.0;
    }

    bool evalCondition(const QString& rawCond) {
        QString c = rawCond.trimmed();
        if (c.isEmpty()) return false;

        int orIdx = findTopLevelOp(c, "||");
        if (orIdx != -1) {
            return evalCondition(c.left(orIdx)) || evalCondition(c.mid(orIdx + 2));
        }
        int andIdx = findTopLevelOp(c, "&&");
        if (andIdx != -1) {
            return evalCondition(c.left(andIdx)) && evalCondition(c.mid(andIdx + 2));
        }

        const char* ops[] = { "<=", ">=", "==", "!=", "<", ">" };
        for (int k = 0; k < 6; ++k) {
            QString op(ops[k]);
            int opIdx = findTopLevelOp(c, op);
            if (opIdx != -1) {
                double lhs = evalExpression(c.left(opIdx));
                double rhs = evalExpression(c.mid(opIdx + op.length()));
                if (op == "<=") return lhs <= rhs;
                if (op == ">=") return lhs >= rhs;
                if (op == "==") return lhs == rhs;
                if (op == "!=") return lhs != rhs;
                if (op == "<") return lhs < rhs;
                if (op == ">") return lhs > rhs;
            }
        }
        return evalExpression(c) != 0.0;
    }

    int findTopLevelOp(const QString& s, const QString& op) const {
        int depth = 0;
        for (int i = 0; i <= s.length() - op.length(); ++i) {
            QChar ch = s[i];
            if (ch == '(' || ch == '[') ++depth;
            else if (ch == ')' || ch == ']') --depth;
            else if (depth == 0 && s.mid(i, op.length()) == op) {
                if ((op == "<" || op == ">") && i + 1 < s.length() && s[i + 1] == '=') {
                    continue;
                }
                return i;
            }
        }
        return -1;
    }

    QString extractSubBody(const QString& str, int startIdx, int& nextIdx) {
        int idx = startIdx;
        int len = str.length();
        while (idx < len && str[idx].isSpace()) ++idx;
        if (idx < len && str[idx] == '{') {
            int depth = 1;
            int j = idx + 1;
            while (j < len && depth > 0) {
                if (str[j] == '{') ++depth;
                else if (str[j] == '}') --depth;
                ++j;
            }
            nextIdx = j;
            return str.mid(idx + 1, j - idx - 2);
        }
        int semi = str.indexOf(';', idx);
        if (semi != -1) {
            nextIdx = semi + 1;
            return str.mid(idx, semi - idx + 1);
        }
        nextIdx = len;
        return "";
    }

    void executeBlock(const QString& blockStr, std::vector<ExecutionStep>& steps) {
        int i = 0;
        int n = blockStr.length();

        while (i < n) {
            while (i < n && blockStr[i].isSpace()) ++i;
            if (i >= n) break;

            QString rem = blockStr.mid(i);

            // while (...)
            if (rem.startsWith("while")) {
                QRegExp rx("^while\\s*\\(");
                if (rx.indexIn(rem) != -1) {
                    int condStart = i + rx.matchedLength();
                    int depth = 1;
                    int kp = condStart;
                    while (kp < n && depth > 0) {
                        if (blockStr[kp] == '(') ++depth;
                        else if (blockStr[kp] == ')') --depth;
                        ++kp;
                    }
                    QString condStr = blockStr.mid(condStart, kp - condStart - 1);
                    QString body = extractSubBody(blockStr, kp, i);
                    runWhileLoop(condStr, body, steps);
                    continue;
                }
            }

            // if (...)
            if (rem.startsWith("if")) {
                QRegExp rx("^if\\s*\\(");
                if (rx.indexIn(rem) != -1) {
                    int condStart = i + rx.matchedLength();
                    int depth = 1;
                    int kp = condStart;
                    while (kp < n && depth > 0) {
                        if (blockStr[kp] == '(') ++depth;
                        else if (blockStr[kp] == ')') --depth;
                        ++kp;
                    }
                    QString condStr = blockStr.mid(condStart, kp - condStart - 1);
                    QString body = extractSubBody(blockStr, kp, i);
                    runIfCondition(condStr, body, steps);
                    continue;
                }
            }

            // for (...)
            if (rem.startsWith("for")) {
                QRegExp rx("^for\\s*\\(");
                if (rx.indexIn(rem) != -1) {
                    int condStart = i + rx.matchedLength();
                    int depth = 1;
                    int kp = condStart;
                    while (kp < n && depth > 0) {
                        if (blockStr[kp] == '(') ++depth;
                        else if (blockStr[kp] == ')') --depth;
                        ++kp;
                    }
                    QString header = blockStr.mid(condStart, kp - condStart - 1);
                    QString body = extractSubBody(blockStr, kp, i);
                    runForLoop(header, body, steps);
                    continue;
                }
            }

            int semiPos = blockStr.indexOf(';', i);
            QString stmt;
            if (semiPos == -1) {
                stmt = blockStr.mid(i).trimmed();
                i = n;
            } else {
                stmt = blockStr.mid(i, semiPos - i).trimmed();
                i = semiPos + 1;
            }

            if (!stmt.isEmpty()) {
                executeStatement(stmt, steps);
            }
        }
    }

    void runWhileLoop(const QString& condStr, const QString& bodyStr, std::vector<ExecutionStep>& steps) {
        int safety = 0;
        while (safety < 1000 && evalCondition(condStr)) {
            if (m_foundIndex >= 0 && bodyStr.contains("break")) break;
            pushScope();
            executeBlock(bodyStr, steps);
            popScope();
            ++safety;
        }
    }

    void runForLoop(const QString& header, const QString& body, std::vector<ExecutionStep>& steps) {
        QStringList parts = header.split(';');
        if (parts.size() != 3) return;

        QString initPart = parts[0].trimmed();
        QString condPart = parts[1].trimmed();
        QString incPart = parts[2].trimmed();

        pushScope();

        if (initPart.contains('=')) {
            int eq = initPart.indexOf('=');
            QString lhs = initPart.left(eq).trimmed();
            QString rhs = initPart.mid(eq + 1).trimmed();
            QStringList tokens = lhs.split(QRegularExpression("\\s+"), Qt::SkipEmptyParts);
            QString varName = tokens.isEmpty() ? lhs : tokens.last();
            setVar(varName, evalExpression(rhs), true);
        }

        int safety = 0;
        while (safety < 1000 && evalCondition(condPart)) {
            if (m_foundIndex >= 0 && body.contains("break")) break;

            executeBlock(body, steps);

            if (incPart.contains("++")) {
                QString vname = incPart;
                vname.remove("++");
                vname = vname.trimmed();
                setVar(vname, getVar(vname) + 1.0);
            } else if (incPart.contains("--")) {
                QString vname = incPart;
                vname.remove("--");
                vname = vname.trimmed();
                setVar(vname, getVar(vname) - 1.0);
            } else if (incPart.contains("+=")) {
                int idx = incPart.indexOf("+=");
                QString vname = incPart.left(idx).trimmed();
                double stepVal = evalExpression(incPart.mid(idx + 2));
                setVar(vname, getVar(vname) + stepVal);
            }
            ++safety;
        }

        popScope();
    }

    void runIfCondition(const QString& condExpr, const QString& bodyStmt, std::vector<ExecutionStep>& steps) {
        bool condResult = evalCondition(condExpr);
        QString condLow = condExpr.toLower();

        bool isBinaryMatch = condLow.contains("mid") && condExpr.contains("==");
        bool isSearchCond = (condLow.contains("target") || condLow.contains("key")) &&
                            condExpr.contains("==") && !isBinaryMatch;
        bool isMinCond = condLow.contains("min") && (condExpr.contains('<') || condExpr.contains('>'));
        bool isMaxCond = condLow.contains("max") && (condExpr.contains('>') || condExpr.contains('<'));
        bool isSortCond = !isMinCond && !isMaxCond &&
                          condExpr.contains(QRegularExpression("\\[[^\\]]+\\]\\s*[><]\\s*[^\\[]*\\[[^\\]]+\\]"));

        int currI = -1;
        QRegExp idxRx("\\[\\s*(\\w+)\\s*\\]");
        if (idxRx.indexIn(condExpr) != -1) {
            QString rawV = idxRx.cap(1);
            currI = hasVar(rawV) ? static_cast<int>(getVar(rawV)) : rawV.toInt();
        }

        if (isSearchCond && currI >= 0) {
            m_searchIndex = currI;
        }

        if (isSortCond) {
            std::vector<int> idxs;
            int pos = 0;
            while ((pos = idxRx.indexIn(condExpr, pos)) != -1) {
                idxs.push_back(static_cast<int>(evalExpression(idxRx.cap(1))));
                pos += idxRx.matchedLength();
            }
            if (idxs.size() >= 2) {
                m_activePair.clear();
                m_activePair.push_back(idxs[0]);
                m_activePair.push_back(idxs[1]);
            }
        }

        if (condResult) {
            if (isBinaryMatch) {
                m_foundIndex = static_cast<int>(getVar("mid"));
                steps.push_back(makeStep("Двійковий пошук: ЕЛЕМЕНТ ЗНАЙДЕНО на позиції [" +
                                         toQStr(m_foundIndex) + "]!"));
            } else if (isSearchCond && currI >= 0) {
                m_foundIndex = currI;
                steps.push_back(makeStep("Лінійний пошук: ЕЛЕМЕНТ ЗНАЙДЕНО [" + toQStr(currI) + "]!"));
            } else if (isSortCond) {
                steps.push_back(makeStep("Сортування: умова (" + condExpr + ") -> ТАК. Обмін!"));
            }

            pushScope();
            executeBlock(bodyStmt, steps);
            popScope();

            if (hasVar("low") && hasVar("high")) {
                m_hasBinaryRange = true;
                m_binaryLow = static_cast<int>(getVar("low"));
                m_binaryHigh = static_cast<int>(getVar("high"));
            }

            if (isMaxCond && m_arrays.count(m_mainArrayName)) {
                const std::vector<double>& arr = m_arrays[m_mainArrayName];
                for (std::size_t s = 0; s < m_scopes.size(); ++s) {
                    for (std::map<QString, double>::const_iterator it = m_scopes[s].begin();
                         it != m_scopes[s].end(); ++it) {
                        if (it->first.toLower().contains("max")) {
                            m_hasMaxVal = true;
                            if (it->first.toLower().contains("index") || it->first.toLower().contains("idx")) {
                                int idx = static_cast<int>(it->second);
                                if (idx >= 0 && idx < static_cast<int>(arr.size())) {
                                    m_currentMaxVal = arr[static_cast<std::size_t>(idx)];
                                }
                            } else {
                                m_currentMaxVal = it->second;
                            }
                            m_maxIndices.clear();
                            for (std::size_t k = 0; k < arr.size(); ++k) {
                                if (arr[k] == m_currentMaxVal) {
                                    m_maxIndices.push_back(static_cast<int>(k));
                                }
                            }
                        }
                    }
                }
                steps.push_back(makeStep("Знайдено новий максимум: " + toQStr(m_currentMaxVal, m_precision)));
            } else if (isMinCond && m_arrays.count(m_mainArrayName)) {
                const std::vector<double>& arr = m_arrays[m_mainArrayName];
                for (std::size_t s = 0; s < m_scopes.size(); ++s) {
                    for (std::map<QString, double>::const_iterator it = m_scopes[s].begin();
                         it != m_scopes[s].end(); ++it) {
                        if (it->first.toLower().contains("min") && !it->first.toLower().contains("max")) {
                            m_hasMinVal = true;
                            if (it->first.toLower().contains("index") || it->first.toLower().contains("idx")) {
                                int idx = static_cast<int>(it->second);
                                if (idx >= 0 && idx < static_cast<int>(arr.size())) {
                                    m_currentMinVal = arr[static_cast<std::size_t>(idx)];
                                }
                            } else {
                                m_currentMinVal = it->second;
                            }
                            m_minIndices.clear();
                            for (std::size_t k = 0; k < arr.size(); ++k) {
                                if (arr[k] == m_currentMinVal) {
                                    m_minIndices.push_back(static_cast<int>(k));
                                }
                            }
                        }
                    }
                }
                steps.push_back(makeStep("Знайдено новий мінімум: " + toQStr(m_currentMinVal, m_precision)));
            }
        } else {
            if (isSearchCond && currI >= 0) {
                steps.push_back(makeStep("Лінійний пошук: перевірка [" + toQStr(currI) + "]"));
            } else if (isSortCond) {
                steps.push_back(makeStep("Сортування: умова (" + condExpr + ") -> НІ."));
                m_activePair.clear();
            }
        }
    }

    void executeStatement(const QString& rawStmt, std::vector<ExecutionStep>& steps) {
        QString s = rawStmt.trimmed();
        if (s.isEmpty() || s.startsWith("cout") || s.startsWith("std::cout") || s.startsWith("return")) {
            return;
        }

        // 1. Класичний масив C++98: int A[8] = { 37, 0, 50, ... };
        QRegExp cArrRx("^(?:const\\s+)?(?:int|double|float|long|short|char)\\s+([a-zA-Z_]\\w*)\\s*\\[([^\\]]*)\\]\\s*(?:=\\s*\\{([^}]*)\\})?$");
        if (cArrRx.indexIn(s) != -1) {
            QString name = cArrRx.cap(1);
            QString szStr = cArrRx.cap(2).trimmed();
            QString initStr = cArrRx.cap(3).trimmed();

            std::vector<double> initVals;
            if (!initStr.isEmpty()) {
                QStringList items = initStr.split(',', Qt::SkipEmptyParts);
                for (int k = 0; k < items.size(); ++k) {
                    initVals.push_back(evalExpression(items[k]));
                }
            }

            int sz = !szStr.isEmpty() ? static_cast<int>(evalExpression(szStr))
                                      : static_cast<int>(initVals.size());
            if (sz < 0) sz = 0;
            if (sz > 30) sz = 30;

            std::vector<double> arr(static_cast<std::size_t>(sz), 0.0);
            for (std::size_t k = 0; k < initVals.size() && k < arr.size(); ++k) {
                arr[k] = initVals[k];
            }

            registerArray(name, arr);
            setVar("N", sz, true);
            setVar("n", sz, true);
            m_currentCapacity = sz;
            m_currentSize = sz;
            steps.push_back(makeStep("Оголошено масив: " + name + "[" + toQStr(sz) + "]"));
            return;
        }

        // 2. std::vector<T> v; або std::vector<T> v(n, val);
        QRegExp vecRx("^(?:std\\s*::\\s*)?vector\\s*<[^>]+>\\s*([a-zA-Z_]\\w*)\\s*(?:\\(([^)]*)\\))?$");
        if (vecRx.indexIn(s) != -1) {
            QString name = vecRx.cap(1);
            QString argsStr = vecRx.cap(2).trimmed();
            std::vector<double> arr;
            if (!argsStr.isEmpty()) {
                QStringList args = argsStr.split(',');
                int sz = static_cast<int>(evalExpression(args[0]));
                double fillVal = (args.size() > 1) ? evalExpression(args[1]) : 0.0;
                if (sz > 0 && sz <= 30) {
                    arr.resize(static_cast<std::size_t>(sz), fillVal);
                }
            }
            registerArray(name, arr);
            m_vectorCapacities[name] = static_cast<int>(arr.size());
            m_currentCapacity = static_cast<int>(arr.size());
            m_currentSize = static_cast<int>(arr.size());
            steps.push_back(makeStep("Оголошено std::vector: " + name + "[" + toQStr(m_currentSize) + "]"));
            return;
        }

        // 3. v.push_back(val)
        QRegExp pushRx("^([a-zA-Z_]\\w*)\\.push_back\\s*\\((.+)\\)$");
        if (pushRx.indexIn(s) != -1) {
            QString name = pushRx.cap(1);
            double val = evalExpression(pushRx.cap(2));
            if (m_arrays.count(name)) {
                std::vector<double>& arr = m_arrays[name];
                arr.push_back(val);
                m_mainArrayName = name;
                m_currentSize = static_cast<int>(arr.size());
                int cap = m_vectorCapacities[name];
                if (m_currentSize > cap) {
                    cap = (cap == 0) ? 1 : cap * 2;
                    while (m_currentSize > cap) cap *= 2;
                }
                m_vectorCapacities[name] = cap;
                m_currentCapacity = cap;
                m_activePair.clear();
                m_activePair.push_back(m_currentSize - 1);
                steps.push_back(makeStep(name + ".push_back(" + toQStr(val, m_precision) + ")"));
            }
            return;
        }

        // 4. v.pop_back()
        QRegExp popRx("^([a-zA-Z_]\\w*)\\.pop_back\\s*\\(\\s*\\)$");
        if (popRx.indexIn(s) != -1) {
            QString name = popRx.cap(1);
            if (m_arrays.count(name) && !m_arrays[name].empty()) {
                double popped = m_arrays[name].back();
                m_arrays[name].pop_back();
                m_mainArrayName = name;
                m_currentSize = static_cast<int>(m_arrays[name].size());
                m_currentCapacity = m_vectorCapacities[name];
                m_activePair.clear();
                steps.push_back(makeStep(name + ".pop_back() (вилучено " + toQStr(popped, m_precision) + ")"));
            }
            return;
        }

        // 5. std::swap(a[i], a[j])
        QRegExp swapRx("^(?:std\\s*::\\s*)?swap\\s*\\(\\s*([a-zA-Z_]\\w*)\\[([^\\]]+)\\]\\s*,\\s*([a-zA-Z_]\\w*)\\[([^\\]]+)\\]\\s*\\)$");
        if (swapRx.indexIn(s) != -1) {
            QString n1 = swapRx.cap(1);
            int i1 = static_cast<int>(evalExpression(swapRx.cap(2)));
            QString n2 = swapRx.cap(3);
            int i2 = static_cast<int>(evalExpression(swapRx.cap(4)));
            if (n1 == n2 && m_arrays.count(n1)) {
                std::vector<double>& arr = m_arrays[n1];
                if (i1 >= 0 && i1 < static_cast<int>(arr.size()) &&
                    i2 >= 0 && i2 < static_cast<int>(arr.size())) {
                    m_activePair.clear();
                    m_activePair.push_back(i1);
                    m_activePair.push_back(i2);
                    std::swap(arr[static_cast<std::size_t>(i1)], arr[static_cast<std::size_t>(i2)]);
                    steps.push_back(makeStep("swap(" + n1 + "[" + toQStr(i1) + "], " +
                                             n1 + "[" + toQStr(i2) + "])"));
                    m_activePair.clear();
                }
            }
            return;
        }

        // 6. Присвоєння елементу масиву: A[idx] = val
        QRegExp arrAssignRx("^([a-zA-Z_]\\w*)\\[([^\\]]+)\\]\\s*=\\s*(.+)$");
        if (arrAssignRx.indexIn(s) != -1) {
            QString name = arrAssignRx.cap(1);
            int idx = static_cast<int>(evalExpression(arrAssignRx.cap(2)));
            QString rhs = arrAssignRx.cap(3).trimmed();
            double val = evalExpression(rhs);

            if (m_arrays.count(name)) {
                std::vector<double>& arr = m_arrays[name];
                if (idx >= 0 && idx < static_cast<int>(arr.size())) {
                    double old = arr[static_cast<std::size_t>(idx)];
                    arr[static_cast<std::size_t>(idx)] = val;
                    if (rhs.toLower().contains("temp")) {
                        steps.push_back(makeStep(name + "[" + toQStr(idx) + "] = temp (" +
                                                 toQStr(val, m_precision) + ")"));
                        m_hasTempVal = false;
                        m_activePair.clear();
                    } else {
                        steps.push_back(makeStep(name + "[" + toQStr(idx) + "] = " +
                                                 toQStr(val, m_precision) + " (було " +
                                                 toQStr(old, m_precision) + ")"));
                    }
                }
            }
            return;
        }

        // 7. Інкремент / декремент змінних: count++, ++i
        QRegExp incRx("^(\\+\\+|--)?([a-zA-Z_]\\w*)(\\+\\+|--)?$");
        if (incRx.indexIn(s) != -1) {
            QString vname = incRx.cap(2);
            QString op = !incRx.cap(1).isEmpty() ? incRx.cap(1) : incRx.cap(3);
            if (!op.isEmpty()) {
                double nv = getVar(vname) + ((op == "++") ? 1.0 : -1.0);
                setVar(vname, nv);
                if (vname.toLower().contains("count")) {
                    m_hasConditionCount = true;
                    m_conditionCount = static_cast<int>(nv);
                    steps.push_back(makeStep("Лічильник " + vname + " = " + toQStr(m_conditionCount)));
                }
            }
            return;
        }

        // 8. Накопичення sum += val
        QRegExp plusEqRx("^([a-zA-Z_]\\w*)\\s*(\\+=|-=)\\s*(.+)$");
        if (plusEqRx.indexIn(s) != -1) {
            QString vname = plusEqRx.cap(1);
            QString op = plusEqRx.cap(2);
            double addVal = evalExpression(plusEqRx.cap(3));
            double nv = getVar(vname) + ((op == "+=") ? addVal : -addVal);
            setVar(vname, nv);
            if (vname.toLower().contains("sum")) {
                steps.push_back(makeStep("Накопичення суми: " + vname + " = " + toQStr(nv, m_precision)));
            }
            return;
        }

        // 9. Оголошення або присвоєння скалярної змінної
        QRegExp varRx("^(?:(?:const|long|short|char|int|double|float|bool|size_t)\\s+)*([a-zA-Z_]\\w*)\\s*(?:=\\s*(.+))?$");
        if (varRx.indexIn(s) != -1) {
            QString vname = varRx.cap(1);
            QString rhs = varRx.cap(2).trimmed();
            bool isDecl = s.contains(QRegularExpression("\\b(?:int|double|float|bool|long|short|char|size_t)\\b"));
            double val = rhs.isEmpty() ? 0.0 : evalExpression(rhs);
            setVar(vname, val, isDecl);

            if (vname.toLower().contains("temp")) {
                m_hasTempVal = true;
                m_tempVal = val;
                steps.push_back(makeStep("Збереження в буфер: temp = " + toQStr(val, m_precision)));
            } else if (vname.toLower() == "mid") {
                m_binaryMid = static_cast<int>(val);
                m_hasBinaryRange = true;
                m_binaryLow = static_cast<int>(getVar("low"));
                m_binaryHigh = static_cast<int>(getVar("high"));
                steps.push_back(makeStep("Двійковий пошук: mid = " + toQStr(m_binaryMid)));
            } else if (vname.toLower() == "low" || vname.toLower() == "high") {
                m_hasBinaryRange = true;
                m_binaryLow = static_cast<int>(getVar("low"));
                m_binaryHigh = static_cast<int>(getVar("high"));
                steps.push_back(makeStep("Двійковий пошук: діапазон [" + toQStr(m_binaryLow) +
                                         "..." + toQStr(m_binaryHigh) + "]"));
            } else if (vname.toLower().contains("max") && m_arrays.count(m_mainArrayName)) {
                m_hasMaxVal = true;
                m_currentMaxVal = val;
                steps.push_back(makeStep("Ініціалізація максимуму: " + vname + " = " + toQStr(val, m_precision)));
            } else if (vname.toLower().contains("min") && !vname.toLower().contains("max") &&
                       m_arrays.count(m_mainArrayName)) {
                m_hasMinVal = true;
                m_currentMinVal = val;
                steps.push_back(makeStep("Ініціалізація мінімуму: " + vname + " = " + toQStr(val, m_precision)));
            }
        }
    }
};

// ============================================================================
// ГОЛОВНИЙ ВІДЖЕТ ВІЗУАЛІЗАТОРА CodeVisualizer (ідентично Project 2.py)
// ============================================================================
class CodeVisualizer : public QWidget {
    Q_OBJECT

public:
    explicit CodeVisualizer(QWidget* parent = 0)
        : QWidget(parent),
          m_currentStep(0) {
        setWindowTitle("Покрокова візуалізація масивів C++");

        QHBoxLayout* mainLayout = new QHBoxLayout(this);

        // Ліва панель: чисте поле для введення коду C++98 (без вставлених прикладів)
        QVBoxLayout* leftLayout = new QVBoxLayout();
        mainLayout->addLayout(leftLayout, 1);

        m_codeEdit = new QTextEdit(this);
        m_codeEdit->setFont(QFont("Consolas", 12));
        connect(m_codeEdit, SIGNAL(textChanged()), this, SLOT(onCodeTextChanged()));
        leftLayout->addWidget(m_codeEdit);

        // Центральна колонка кнопок: ▶ (Запуск) та ⏹ (Скидання)
        QVBoxLayout* buttonLayout = new QVBoxLayout();
        mainLayout->addLayout(buttonLayout);

        m_runButton = new QPushButton(QString::fromUtf8("\xE2\x96\xB6"), this);
        m_runButton->setFixedSize(42, 42);
        m_runButton->setFont(QFont("Arial", 14, QFont::Bold));
        connect(m_runButton, SIGNAL(clicked()), this, SLOT(runVisualization()));
        buttonLayout->addWidget(m_runButton);

        m_stopButton = new QPushButton(QString::fromUtf8("\xE2\x8F\xB9"), this);
        m_stopButton->setFixedSize(42, 42);
        m_stopButton->setFont(QFont("Arial", 14, QFont::Bold));
        m_stopButton->setToolTip("Скинути стан");
        connect(m_stopButton, SIGNAL(clicked()), this, SLOT(resetVisualizer()));
        buttonLayout->addWidget(m_stopButton);

        buttonLayout->addStretch();

        // Права панель: графічна сцена анімації
        m_animWidget = new AdaptiveAnimationWidget(this);
        mainLayout->addWidget(m_animWidget, 1);

        m_timer = new QTimer(this);
        connect(m_timer, SIGNAL(timeout()), this, SLOT(processNextStep()));
    }

private slots:
    void onCodeTextChanged() {
        if (m_codeEdit->toPlainText().trimmed().isEmpty()) {
            resetVisualizer();
        }
    }

    void resetVisualizer() {
        m_timer->stop();
        m_animWidget->reset();
        m_stepsQueue.clear();
        m_currentStep = 0;
    }

    void runVisualization() {
        QString codeText = m_codeEdit->toPlainText().trimmed();
        if (codeText.isEmpty()) {
            resetVisualizer();
            return;
        }

        m_timer->stop();
        m_animWidget->reset();
        m_currentStep = 0;

        m_stepsQueue = m_engine.run(codeText);
        if (m_stepsQueue.empty()) {
            return;
        }

        // step_delay = 450 мс, тривалість анімації <= 350 мс (п. 4 ТЗ)
        m_animWidget->setAnimationSpeed(450);
        processNextStep();
        m_timer->start(450);
    }

    void processNextStep() {
        if (m_currentStep >= m_stepsQueue.size()) {
            m_timer->stop();
            return;
        }

        m_animWidget->updateVariables(m_stepsQueue[m_currentStep]);
        ++m_currentStep;
    }

private:
    QTextEdit* m_codeEdit;
    QPushButton* m_runButton;
    QPushButton* m_stopButton;
    AdaptiveAnimationWidget* m_animWidget;
    QTimer* m_timer;

    std::vector<ExecutionStep> m_stepsQueue;
    std::size_t m_currentStep;
    CppUniversalEngine m_engine;
};

int main(int argc, char* argv[]) {
    QApplication app(argc, argv);
    CodeVisualizer window;
    window.resize(1100, 650);
    window.show();
    return app.exec();
}
