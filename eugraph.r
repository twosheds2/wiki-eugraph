# Load necessary libraries
library(ggplot2)
library(ggrepel)
library(tidyr)
library(scales)
library(lubridate)
library(tidyverse)

# Read the CSV file
data <- read.csv("output.csv")

# Convert end_date to a date format if necessary
data$end_date <- as.Date(data$end_date, format = "%Y-%m-%d")

# Reshape the data to long format for ggplot2
long_data <- pivot_longer(data, cols = c("rejoin", "stay_out", "neither"), 
                          names_to = "category", values_to = "value")

long_data <- long_data %>%
  mutate(category = recode(category, 
                          "rejoin" = "Rejoin", 
                          "stay_out" = "Stay out", 
                          "neither" = "Neither"))

# Calculate where to put labels
labelInfo <-
  split(long_data, long_data$category) %>%

  lapply(function(t) {
    t$end_date <- as.numeric(t$end_date) 
    data.frame(
      predAtMax = loess(value ~ end_date, span = 0.4, data = t) %>%
        predict(newdata = data.frame(end_date = max(t$end_date)))
      , max = max(t$end_date)
    )}) %>%
  bind_rows
labelInfo$max <- as.Date(labelInfo$max, origin = "1970-01-01")
labelInfo$label = levels(factor(long_data$category))

# Create the scatterplot
ggplot(long_data, aes(x = end_date, y = value, color = category)) +
     geom_point(alpha = .5, size = 1) +
     geom_smooth(method = "loess",
                    formula = y ~ x,
                    se = FALSE,
                    n = 1000,
                    span = 0.4,
                    alpha = 0) +
     scale_color_manual(values = c(
               "Rejoin" = "#4477AA",
               "Stay out" = "#EE6677",
               "Neither" = "#BCBCBC"
          )) +
     scale_y_continuous(labels = percent_format(accuracy = 1),
                         breaks = seq(from = 0, to = .6, .1),   # Set breaks on Y axis - update if changing limits in line below
                         limits = c(-.01, 0.6 + .01),           # Set max 60% on graph
                         expand = c(0, 0)) +
     scale_x_date(date_labels = "%b %Y",
                    breaks = seq(from = ymd("2020-01-01"), to = ymd("2025-12-01"), by = "6 months"),    # Y axis breaks - update if changing limits below
                    date_minor_breaks = "1 month",
                    limits = c(ymd("2019-12-01"), ymd("2026-02-01")),  # Sets the date range on the X axis
                                                                       # Change second date to around 6 months in future when re-running
                    expand = c(0, 0)) +
     geom_label_repel(data = labelInfo,
                   aes(x = max, y = predAtMax, 
                       label = label, 
                       color = label), 
                   nudge_x = 5, 
                   label.size = 0,
                   label.padding = unit(0, "lines"),
                   fill = "transparent",
                   size = 6) +
     theme(plot.margin = unit(c(1,1,.5,1), "lines"),
          panel.background = element_rect(fill = "#EEEEEE"),
          legend.position = "none",
          axis.title.x = element_blank(),
          axis.title.y = element_blank(),
          axis.text = element_text(size = 12))

ggsave("Opinion_polling_on_the_whether_the_United_Kingdom_should_rejoin_the_European_Union.svg", scale=0.4, width=720, height=420, units = "mm", bg="#FFFFFF")