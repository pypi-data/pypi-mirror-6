/*
    Copyright (c) 2007-2013 Contributors as noted in the AUTHORS file

    This file is part of 0MQ.

    0MQ is free software; you can redistribute it and/or modify it under
    the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    0MQ is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef __ZMQ_PGM_SENDER_HPP_INCLUDED__
#define __ZMQ_PGM_SENDER_HPP_INCLUDED__

#include "platform.hpp"

#if defined ZMQ_HAVE_OPENPGM

#ifdef ZMQ_HAVE_WINDOWS
#include "windows.hpp"
#endif

#include "stdint.hpp"
#include "io_object.hpp"
#include "i_engine.hpp"
#include "options.hpp"
#include "pgm_socket.hpp"
#include "v1_encoder.hpp"
#include "msg.hpp"

namespace zmq
{

    class io_thread_t;
    class session_base_t;

    class pgm_sender_t : public io_object_t, public i_engine
    {

    public:

        pgm_sender_t (zmq::io_thread_t *parent_, const options_t &options_);
        ~pgm_sender_t ();

        int init (bool udp_encapsulation_, const char *network_);

        //  i_engine interface implementation.
        void plug (zmq::io_thread_t *io_thread_,
            zmq::session_base_t *session_);
        void terminate ();
        void restart_input ();
        void restart_output ();
        void zap_msg_available () {}

        //  i_poll_events interface implementation.
        void in_event ();
        void out_event ();
        void timer_event (int token);

    private:

        //  Unplug the engine from the session.
        void unplug ();

        //  TX and RX timeout timer ID's.
        enum {tx_timer_id = 0xa0, rx_timer_id = 0xa1};

        //  Timers are running.
        bool has_tx_timer;
        bool has_rx_timer;

        session_base_t *session;

        //  Message encoder.
        v1_encoder_t encoder;

        msg_t msg;

        //  Keeps track of message boundaries.
        bool more_flag;

        //  PGM socket.
        pgm_socket_t pgm_socket;

        //  Socket options.
        options_t options;

        //  Poll handle associated with PGM socket.
        handle_t handle;
        handle_t uplink_handle;
        handle_t rdata_notify_handle;
        handle_t pending_notify_handle;

        //  Output buffer from pgm_socket.
        unsigned char *out_buffer;
        
        //  Output buffer size.
        size_t out_buffer_size;

        //  Number of bytes in the buffer to be written to the socket.
        //  If zero, there are no data to be sent.
        size_t write_size;

        pgm_sender_t (const pgm_sender_t&);
        const pgm_sender_t &operator = (const pgm_sender_t&);
    };

}
#endif

#endif
