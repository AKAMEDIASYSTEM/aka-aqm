#!/bin/bash
cp eink.service /etc/systemd/system/
cp eink.timer /etc/systemd/system/
systemctl enable eink.timer
systemctl start eink.timer
systemctl enable eink.service
systemctl start eink.service