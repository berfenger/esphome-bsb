#pragma once

#include "bsb.h"
#include "bsbPacket.h"

#include "esphome/components/button/button.h"
#include "esphome/components/time/real_time_clock.h"
#include "esphome/core/log.h"

namespace esphome {
  namespace bsb {

    static const char* const BUTTON_TAG = "bsb.button";

    class BsbDatetimeSyncButton : public button::Button, public Component {
    public:
      void set_field_id( const uint32_t field_id ) { this->field_id_ = field_id; }
      void set_bsb_component( BsbComponent* component ) { this->bsb_component_ = component; }
      void set_time_component( time::RealTimeClock* time_component ) { this->time_component_ = time_component; }

      void press_action() override {
        if( this->time_component_ == nullptr || this->bsb_component_ == nullptr ) {
          ESP_LOGE( BUTTON_TAG, "Time or BSB component not set" );
          return;
        }

        auto now = this->time_component_->now();
        if( !now.is_valid() ) {
          ESP_LOGE( BUTTON_TAG, "Time not yet synchronized" );
          return;
        }

        ESP_LOGI( BUTTON_TAG, "Syncing datetime to heater: %04d-%02d-%02d %02d:%02d:%02d",
                  now.year, now.month, now.day_of_month,
                  now.hour, now.minute, now.second );

        BsbPacket packet;
        packet.sourceAddress      = this->bsb_component_->get_source_address();
        packet.destinationAddress = this->bsb_component_->get_destination_address();
        packet.command            = BsbPacket::Command::Set;
        packet.fieldId            = this->field_id_;

        // Build datetime payload (9 bytes)
        // Byte 0: enable_byte (0x01)
        // Byte 1: year - 1900
        // Byte 2: month
        // Byte 3: day
        // Byte 4: day of week (1=Mon, 7=Sun in ESPHome, BSB uses 0=Mon, 6=Sun)
        // Byte 5: hour
        // Byte 6: minute
        // Byte 7: second
        // Byte 8: date_flag (0x00 for VT_DATETIME)
        packet.payload.clear();
        packet.payload.push_back( 0x01 );                              // enable_byte
        packet.payload.push_back( now.year - 1900 );                   // year - 1900
        packet.payload.push_back( now.month );                         // month
        packet.payload.push_back( now.day_of_month );                  // day
        packet.payload.push_back( ( now.day_of_week + 6 ) % 7 );       // day of week (convert 1-7 Mon-Sun to 0-6)
        packet.payload.push_back( now.hour );                          // hour
        packet.payload.push_back( now.minute );                        // minute
        packet.payload.push_back( now.second );                        // second
        packet.payload.push_back( 0x00 );                              // date_flag

        packet.create_packet();
        this->bsb_component_->write_packet( packet );
      }

    protected:
      uint32_t             field_id_;
      BsbComponent*        bsb_component_;
      time::RealTimeClock* time_component_;
    };

  } // namespace bsb
} // namespace esphome
