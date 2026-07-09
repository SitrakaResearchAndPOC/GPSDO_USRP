#!/bin/bash

 ( grep -qF 'static const std::regex gp_msg_regex("^\\$G.*$");' host/lib/usrp/gps_ctrl.cpp ||   sed -i '/static const std::regex gp_msg_regex/{s|^|// |;a\
static const std::regex gp_msg_regex("^\\\\$G.*$");
}' host/lib/usrp/gps_ctrl.cpp ) && ( grep -qF 'if(msg.substr(1,2) == "GN"){ msg.replace(1, 2, "GP");}' host/lib/usrp/gps_ctrl.cpp ||   sed -i '/msgs\[msg\.substr(1, 5)\] = msg;/i\
        if(msg.substr(1,2) == "GN"){ msg.replace(1, 2, "GP");}
' host/lib/usrp/gps_ctrl.cpp )

